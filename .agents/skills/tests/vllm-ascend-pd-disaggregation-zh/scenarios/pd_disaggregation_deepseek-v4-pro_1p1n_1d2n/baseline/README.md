# DeepSeek-V4-Pro PD分离部署包 (1P1N 1D2N)

## 概述

本部署包为 DeepSeek-V4-Pro 模型的 Prefill-Decode 分离架构配置，采用 1 个 Prefill 实例（每实例 1 节点）+ 1 个 Decode 实例（每实例 2 节点）的部署方案。

## 配置参数

| 参数 | 值 |
|------|-----|
| model_name | DeepSeek-V4-Pro |
| version | 0.18.0 |
| machine_type | A3 (Atlas 800 A3, 128G x 8) |
| model_path | /root/.cache/DeepSeek-V4-Pro |
| extra_mounts | /mnt |
| nic_name | eth0 |
| kv_connector | MooncakeHybridConnector |
| proxy_type | 基础版本 |

### 并行参数

| 参数 | 值 | 说明 |
|------|-----|------|
| tp_size | 8 | Tensor Parallel Size (从模板获取) |
| dp_size_local | 2 | Data Parallel Size Local (16/8=2) |
| prefill_dp_size | 2 | Prefill 总 DP (1x1x2) |
| decode_dp_size | 4 | Decode 总 DP (1x2x2) |

### 节点 IP 配置

| 角色 | 实例 | 节点 | IP | kv_port | engine_id | dp_rank_start |
|------|------|------|-----|---------|-----------|---------------|
| Prefill | 1 | 1 | 192.168.1.20 | 36000 | 1 | 0 |
| Decode | 1 | 1 | 192.168.1.30 | 36200 | 2 | 0 |
| Decode | 1 | 2 | 192.168.1.31 | 36200 | 2 | 2 |
| Proxy | - | - | 192.168.1.40 | 1999 | - | - |

## 目录结构

```
pd_disaggregation_deepseek_v4_pro_1p1n_1d2n/
├── sources/                                    # 源模板文件
│   ├── DeepSeek-V4-Pro.md                     # 模型教程文档
│   ├── pd_disaggregation_mooncake_multi_node.md # PD分离理论参考
│   ├── start_container.sh                     # 容器启动脚本模板
│   ├── launch_online_dp.py                    # DP启动脚本
│   ├── run_dp_template_prefill_node1.sh       # Prefill节点1模板
│   ├── run_dp_template_decode_node1.sh        # Decode节点1模板
│   ├── run_dp_template_decode_node2.sh        # Decode节点2模板
│   ├── load_balance_proxy_server_example.py   # 基础版本代理
│   └── load_balance_proxy_layerwise_server_example.py # 分层版本代理
├── prefill/                                    # Prefill部署目录
│   ├── start_container.sh                     # Prefill容器启动脚本
│   └── instance1/
│       └── node1/
│           ├── launch_online_dp.py            # DP启动脚本
│           ├── run_dp_template.sh             # 运行模板脚本
│           └── start_serve.sh                 # 启动服务脚本
├── decode/                                     # Decode部署目录
│   ├── start_container.sh                     # Decode容器启动脚本
│   └── instance1/
│       ├── node1/
│       │   ├── launch_online_dp.py
│       │   ├── run_dp_template.sh
│       │   └── start_serve.sh
│       └── node2/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
├── proxy/                                      # Proxy部署目录
│   ├── load_balance_proxy_server_example.py   # 基础版本代理
│   ├── load_balance_proxy_layerwise_server_example.py # 分层版本代理
│   └── start_proxy.sh                         # Proxy启动脚本
└── README.md                                   # 本文档
```

## 部署步骤

### 1. 启动容器

在每个节点上启动 Docker 容器：

**Prefill 节点：**
```bash
# 在 192.168.1.20 (P1N1) 上执行
cd prefill
bash start_container.sh
```

**Decode 节点：**
```bash
# 在 192.168.1.30 (D1N1) 上执行
cd decode
bash start_container.sh

# 在 192.168.1.31 (D1N2) 上执行
cd decode
bash start_container.sh
```

### 2. 启动 Prefill 服务

在 Prefill 容器内：

**P1N1 (192.168.1.20):**
```bash
cd instance1/node1
bash start_serve.sh
```

### 3. 启动 Decode 服务

在 Decode 容器内：

**D1N1 (192.168.1.30):**
```bash
cd instance1/node1
bash start_serve.sh
```

**D1N2 (192.168.1.31):**
```bash
cd instance1/node2
bash start_serve.sh
```

### 4. 启动 Proxy 服务

在 Proxy 节点 (192.168.1.40) 上：

```bash
cd proxy
bash start_proxy.sh
```

### 5. 测试服务

通过 Proxy 发送请求：

```bash
curl http://192.168.1.40:1999/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "auto",
        "messages": [
            {
                "role": "user",
                "content": "Hello, who are you?"
            }
        ],
        "max_tokens": 256,
        "temperature": 0
    }'
```

## Proxy 配置说明

本部署包使用**基础版本**代理 (load_balance_proxy_server_example.py)。

### Prefill/Decode hosts/ports 配置

| 配置项 | 值 |
|--------|-----|
| PREFILLER_HOSTS | 192.168.1.20 192.168.1.20 |
| PREFILLER_PORTS | 7100 7101 |
| DECODER_HOSTS | 192.168.1.30 192.168.1.30 192.168.1.31 192.168.1.31 |
| DECODER_PORTS | 7100 7101 7100 7101 |

说明：
- 每个节点 IP 重复 `dp_size_local` (2) 次
- 端口从 `vllm_start_port` (7100) 开始，到 7100+dp_size_local-1 (7101)

## KV Transfer 配置

### Prefill 配置
```json
{
  "kv_connector": "MooncakeHybridConnector",
  "kv_role": "kv_producer",
  "kv_port": "36000",
  "engine_id": "1",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": 2, "tp_size": 8},
    "decode": {"dp_size": 4, "tp_size": 8}
  }
}
```

### Decode 配置
```json
{
  "kv_connector": "MooncakeHybridConnector",
  "kv_role": "kv_consumer",
  "kv_port": "36200",
  "engine_id": "2",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": 2, "tp_size": 8},
    "decode": {"dp_size": 4, "tp_size": 8}
  }
}
```

## 工作流执行日志

| 步骤 | 状态 | 时间戳 | 摘要 |
|------|------|--------|------|
| 1. 收集参数 | ✅ 完成 | 2026-05-26 22:40 | 使用预定义参数，跳过交互式问答 |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-26 22:37 | DeepSeek-V4-Pro.md |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-26 22:37 | 找到 Prefill-Decode Disaggregation 章节 |
| 4. 下载文件 | ✅ 完成 | 2026-05-26 22:38-39 | launch_online_dp.py, proxy 脚本 |
| 5. 提取模板 | ✅ 完成 | 2026-05-26 22:40 | A3 格式，prefill/decode 模板 |
| 6. 生成部署树 | ✅ 完成 | 2026-05-26 22:31-33 | prefill/decode/proxy 目录 |
| 7. 验证一致性 | ✅ 完成 | 2026-05-26 22:44 | 参数验证通过 |
| 8. 编写 README | ✅ 完成 | 2026-05-26 22:45 | 文档更新完成 |

**生成时间**：2026-05-26 22:45

### 详细执行记录

**步骤 1：收集参数**
- 使用预定义参数，跳过 AskUserQuestion
- 参数：model_name=DeepSeek-V4-Pro, version=0.18.0, machine_type=A3
- 计算值：dp_size_local=2, prefill_dp_size=2, decode_dp_size=4

**步骤 2：下载基础文件**
- URL: https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/docs/source/tutorials/models/DeepSeek-V4-Pro.md

**步骤 3：检查部署模式支持**
- 章节标题：Prefill-Decode Disaggregation (行 405)
- 支持确认：模型支持 PD 分离部署

**步骤 4：下载文件**
- pd_disaggregation_mooncake_multi_node.md
- load_balance_proxy_server_example.py
- load_balance_proxy_layerwise_server_example.py
- launch_online_dp.py

**步骤 5：提取模板**
- 文档格式：新格式（有 A2/A3 tab-set）
- 机型选择：A3 series
- 提取脚本：start_container.sh, prefill/decode 模板

**步骤 6：生成部署树**
- Prefill: 1 实例 × 1 节点
- Decode: 1 实例 × 2 节点
- kv_port 配置：Prefill 36000, Decode 36200

**步骤 7：验证一致性**
- kv_role 检查：Prefill kv_producer, Decode kv_consumer ✓
- kv_port 检查：Prefill 36000, Decode 36200 ✓
- engine_id 检查：Prefill 1, Decode 2 ✓
- dp_rank_start 检查：P1N1=0, D1N1=0, D1N2=2 ✓

## 参考

- [DeepSeek-V4-Pro 模型教程](sources/DeepSeek-V4-Pro.md)
- [PD分离理论参考](sources/pd_disaggregation_mooncake_multi_node.md)