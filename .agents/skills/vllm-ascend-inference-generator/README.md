# vllm-ascend 推理服务部署脚本生成器

## 概述

本技能集用于生成 vllm-ascend 推理服务部署包，支持三种部署模式：

- **单节点部署**：适用于快速验证和低延迟场景
- **多节点部署**：适用于大模型和高吞吐场景
- **PD 分离部署**：Prefill-Decode 分离架构，适用于高并发场景，支持 KV Cache 传输优化

## 技能架构

```
vllm-ascend-inference-generator-zh (主技能)
├── vllm-ascend-single-node-zh (单节点部署)
├── vllm-ascend-multi-node-zh (多节点部署)
└── vllm-ascend-pd-disaggregation-zh (PD分离部署)
```

### 主技能 (vllm-ascend-inference-generator-zh)

负责模式选择和路由，收集部署模式参数后调用对应的子技能。

**触发条件**：用户请求 vllm-ascend 推理服务部署脚本生成、单节点/多节点/PD 分离部署配置、DeepSeek/Qwen/GLM 推理部署、vllm serve 启动脚本生成。

### 子技能

| 子技能 | 用途 | 独立调用 |
|--------|------|----------|
| vllm-ascend-single-node-zh | 单节点部署 | 支持 |
| vllm-ascend-multi-node-zh | 多节点分布式部署 | 支持 |
| vllm-ascend-pd-disaggregation-zh | PD 分离部署 | 支持 |

## 工作流

### 主技能工作流

```
模式选择 → 调用子技能
```

主技能仅收集部署模式参数，模型名称、版本和其他参数由子技能收集。

### 子技能工作流

每个子技能遵循统一的工作流：

```
1. 收集参数 → 2. 下载基础文件 → 3. 检查部署模式支持 → 4. 提取模板
→ 5. 生成部署树 → 6. 验证一致性 → 7. 编写 README
```

PD 分离部署额外包含「下载文件」步骤。

## PD 分离实现流程原理

### 架构概述

PD 分离（Prefill-Decode Disaggregation）将推理过程拆分为两个独立阶段：

- **Prefill 阶段**：处理 prompt 编码，生成 KV Cache，作为 KV Cache 生产者（kv_producer）
- **Decode 阶段**：处理 token 生成，消费 KV Cache，作为 KV Cache 消费者（kv_consumer）
- **Proxy**：负载均衡代理，协调 Prefill 和 Decode 实例之间的请求路由和 KV Cache 传输

```
┌─────────────┐     KV Cache      ┌─────────────┐
│   Prefill   │ ──────────────────▶│   Decode    │
│ (Producer)  │                    │ (Consumer)  │
└─────────────┘                    └─────────────┘
      │                                  │
      │         ┌─────────┐              │
      └─────────│  Proxy  │──────────────│
                │ (1999)  │
                └─────────┘
```

### 工作流详解

PD 分离部署遵循 8 步工作流：

```
步骤1: 收集参数
  ├── 模型和版本选择
  ├── 硬件平台、路径、网卡配置
  ├── Prefill/Decode 实例数量和节点数
  ├── 代理类型选择
  └── 节点 IP 地址收集（动态生成）

步骤2: 下载基础文件
  └── 从 GitHub 下载模型教程文档

步骤3: 检查部署模式支持
  └── 验证模型是否支持 PD 分离部署

步骤4: 下载文件（PD分离专用）
  ├── pd_disaggregation_mooncake_multi_node.md（理论参考）
  ├── load_balance_proxy_server_example.py（基础代理）
  ├── load_balance_proxy_layerwise_server_example.py（分层代理）
  └── launch_online_dp.py（DP 启动脚本）

步骤5: 提取模板
  └── 从教程文档提取 run_dp_template_prefill/decode_node*.sh 脚本

步骤6: 生成部署树
  ├── Prefill 实例节点目录（含 launch_online_dp.py、run_dp_template.sh、start_serve.sh）
  ├── Decode 实例节点目录（同上）
  └── Proxy 目录（含代理脚本和 start_proxy.sh）

步骤7: 验证一致性
  └── 检查配置参数和脚本一致性

步骤8: 编写 README
  └── 生成部署说明文档
```

### 参数收集流程

#### 预定义参数检测

当检测到以下条件时，跳过交互式问答，直接使用预定义参数：

1. prompt 包含「所有参数已在下方参数表中预定义」标记
2. 存在完整的参数表（含所有必需参数）
3. 参数完整性满足：模型、版本、机型、路径、实例数、节点数、所有 IP 地址

#### 交互式参数收集

若无预定义参数，按批次收集：

| 批次 | 参数 | 说明 |
|------|------|------|
| 第0批 | model_name, version | DeepSeek-V3.1/V4-Pro, GLM5 等 |
| 第1批 | machine_type, model_path, extra_mounts, nic_name | 硬件平台和网络配置 |
| 第2批 | prefill_instances, decode_instances, nodes_per_prefill, nodes_per_decode | 实例拓扑 |
| 第3批 | proxy_type | 基础版本/分层版本 |
| 第4批+ | Prefill/Decode/Proxy IP | 动态生成，每次最多 4 个 |

#### IP 参数命名规则

```
prefill_p{实例号}_n{节点号}_ip  例如：prefill_p1_n1_ip, prefill_p2_n1_ip
decode_d{实例号}_n{节点号}_ip   例如：decode_d1_n1_ip, decode_d2_n1_ip
proxy_ip                       例如：proxy_ip
```

### 参数计算公式

```text
# tp_size 从模板获取，保持原值不变
dp_size_local = 单机卡数 / tp_size

prefill_dp_size = prefill_instances × nodes_per_prefill_instance × dp_size_local
decode_dp_size = decode_instances × nodes_per_decode_instance × dp_size_local

# kv_port 配置（每个实例唯一）
prefill_kv_port = 36000 + instance_index × 100
decode_kv_port = 36000 + prefill_instances × 100 + instance_index × 100

# engine_id（全局递增）
prefill_engine_id = instance_index + 1  # 1, 2, 3...
decode_engine_id = prefill_instances + instance_index + 1

# dp_rank_start（实例内按节点递增，各实例独立计算）
dp_rank_start = (node_index - 1) × dp_size_local
```

#### 示例计算（2P1D，A3，TP=8）

```text
单机卡数 = 16, tp_size = 8
dp_size_local = 16 / 8 = 2

Prefill:
  prefill_dp_size = 2 × 1 × 2 = 4
  P1N1: kv_port=36000, engine_id=1, dp_rank_start=0
  P2N1: kv_port=36100, engine_id=2, dp_rank_start=0

Decode:
  decode_dp_size = 1 × 1 × 2 = 2
  D1N1: kv_port=36200, engine_id=3, dp_rank_start=0
```

### KV Connector 类型

| Connector | 代理脚本 | 路由方向 | 适用场景 |
|-----------|----------|----------|----------|
| MooncakeConnector | load_balance_proxy_server_example.py | P → D 推送 | 简单部署，轮询负载均衡 |
| MooncakeLayerwiseConnector | load_balance_proxy_layerwise_server_example.py | D → P 拉取 | 复杂部署，动态实例管理 |

**配置示例**：

```json
{
  "kv_connector": "MooncakeConnector",
  "kv_role": "kv_producer",
  "kv_port": "36000",
  "engine_id": "1",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": 4, "tp_size": 8},
    "decode": {"dp_size": 2, "tp_size": 8}
  }
}
```

### 输出目录结构

```text
pd_disaggregation_{model}_{P}p{Np}n_{D}d{Nd}n/
├── sources/                          # 源文件（不可修改）
│   ├── {model}.md                    # 模型教程
│   ├── pd_disaggregation_mooncake_multi_node.md
│   ├── launch_online_dp.py
│   ├── run_dp_template_prefill_node*.sh
│   ├── run_dp_template_decode_node*.sh
│   └── load_balance_proxy_server_example.py
├── prefill/
│   ├── start_container.sh            # Docker 容器启动
│   └── instance{N}/node{M}/
│       ├── launch_online_dp.py       # DP 启动脚本
│       ├── run_dp_template.sh        # vllm serve 启动脚本
│       └── start_serve.sh            # 聚合启动脚本
├── decode/
│   ├── start_container.sh
│   └── instance{N}/node{M}/
│       └── ...                       # 同 Prefill
├── proxy/
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_proxy.sh                # Proxy 启动脚本
└── README.md                         # 部署说明文档
```

### 代理 hosts/ports 配置

Proxy 启动参数格式：

```bash
python load_balance_proxy_server_example.py \
  --port 1999 \
  --host {proxy_ip} \
  --prefiller-hosts {P1N1_IP}×dp_size_local {P1N2_IP}×dp_size_local ... \
  --prefiller-ports 7100 7101 ... 7100+dp_size_local-1 (重复) \
  --decoder-hosts {D1N1_IP}×dp_size_local ... \
  --decoder-ports 7100 7101 ... 7100+dp_size_local-1 (重复)
```

**生成规则**：遍历所有节点，每个节点 IP 重复 `dp_size_local` 次，端口从 7100 开始递增。

## 支持的模型

- DeepSeek 系列
- GLM 系列
- Llama3 系列

## 支持的硬件平台

| 机型 | 卡数 |
|------|------|
| A3 超节点 (Atlas 900 A3) | 16 |
| A2 (Atlas 800 A2) | 8 |

## 使用方式

### 触发主技能

直接请求部署脚本生成，主技能会引导选择部署模式：

```
帮我生成 vllm-ascend 推理部署脚本
```

### 直接调用子技能

明确指定部署模式时，可直接调用对应子技能：

```
生成单节点 vllm-ascend 部署脚本
生成多节点 vllm-ascend 部署脚本
生成 PD 分离 vllm-ascend 部署脚本
```

## 目录结构

```
.agents/skills/vllm-ascend-inference-generator/
├── README.md                                              # 本文件
├── vllm-ascend-inference-generator-zh/
│   ├── SKILL.md                                          # 主技能定义
│   └── references/
│       └── mode-selection.md                             # 模式选择参考
├── vllm-ascend-single-node-zh/
│   ├── SKILL.md                                          # 单节点技能定义
│   └── references/
│       ├── step-01-inputs.md                             # 参数收集
│       ├── step-02-download-base.md                      # 下载基础文件
│       ├── step-03-support-check.md                      # 支持性检查
│       ├── step-05-extract.md                             # 提取模板
│       ├── step-06-generate.md                           # 生成部署树
│       ├── step-07-validate.md                           # 验证一致性
│       └── step-08-readme.md                              # 编写 README
├── vllm-ascend-multi-node-zh/
│   ├── SKILL.md                                          # 多节点技能定义
│   └── references/
│       └── ...                                           # 同上
└── vllm-ascend-pd-disaggregation-zh/
    ├── SKILL.md                                          # PD分离技能定义
    └── references/
        ├── ...                                           # 同上
        └── appendix-pd-resources.md                      # PD专用参考
```

## 输出产物

生成的部署包包含：

- 启动脚本
- 环境变量配置
- 部署说明文档 (README.md)

## 版本支持

| 版本 | GitHub 分支 | GitHub 标签 |
|------|-------------|--------------|
| latest | main | - |
| 0.18.0 | releases/v0.18.0 | v0.18.0 |
| 0.17.0 | releases/v0.17.0 | v0.17.0 |

## 参考

- [vllm-ascend 官方仓库](https://github.com/vllm-project/vllm-ascend)