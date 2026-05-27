# DeepSeek-V4-Pro PD分离部署包 (2P2N 1D2N)

## Deployment Overview

**部署模式**：Prefill-Decode 分离部署

**架构说明**：Prefill 实例处理预填充阶段，Decode 实例处理解码阶段，代理负责负载均衡和 KV Cache 传输。

**配置**：
- Prefill 实例数：2
- Decode 实例数：1
- 每个Prefill实例节点数：2
- 每个Decode实例节点数：2

## Hardware and Software Requirements

| 项目 | 规格 |
|---|---|
| 机型 | A3 超节点 (Atlas 900 A3) |
| 单机卡数 | 16 |
| Prefill 实例 | 2 个 × 2 节点 = 4 节点 |
| Decode 实例 | 1 个 × 2 节点 = 2 节点 |
| 总节点数 | 6 |

**参数计算**：
- tp_size = 8 (从模板获取)
- dp_size_local = 16 / 8 = 2
- prefill_dp_size = 2 × 2 × 2 = 8
- decode_dp_size = 1 × 2 × 2 = 4

## Image Information

| 项目 | 值 |
|---|---|
| 镜像名称 | quay.io/ascend/vllm-ascend:deepseekv4-a3 |
| vllm-ascend 版本 | 0.18.0 |

## Container Startup Instructions

每个节点需要先启动容器，然后启动推理服务。

### 启动容器

```bash
cd prefill/instance{N}/node{M}  # 或 decode/instance{N}/node{M}
./start_container.sh
```

### 启动服务

```bash
./start_serve.sh
```

## Source File Origins

| 文件 | 来源 URL |
|---|---|
| DeepSeek-V4-Pro.md | https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/docs/source/tutorials/models/DeepSeek-V4-Pro.md |
| launch_online_dp.py | https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/examples/external_online_dp/launch_online_dp.py |
| load_balance_proxy_server_example.py | https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py |
| load_balance_proxy_layerwise_server_example.py | https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/examples/disaggregated_prefill_v1/load_balance_proxy_layerwise_server_example.py |

## Startup Sequence

**重要**：必须按 Prefill → Decode → Proxy 顺序启动。

### 1. 启动所有 Prefill 实例节点

```bash
# Prefill 实例 1
cd prefill/instance1/node1
./start_container.sh
./start_serve.sh

cd prefill/instance1/node2
./start_container.sh
./start_serve.sh

# Prefill 实例 2
cd prefill/instance2/node1
./start_container.sh
./start_serve.sh

cd prefill/instance2/node2
./start_container.sh
./start_serve.sh
```

### 2. 启动所有 Decode 实例节点

```bash
# Decode 实例 1
cd decode/instance1/node1
./start_container.sh
./start_serve.sh

cd decode/instance1/node2
./start_container.sh
./start_serve.sh
```

### 3. 启动代理

```bash
cd proxy
./start_proxy.sh
```

## Proxy Configuration

### 代理类型选择

本次部署使用 **分层版本** 代理 (MooncakeHybridConnector)。

| 类型 | kv_connector | 路由方向 | 适用场景 |
|---|---|---|---|
| 基础版本 | MooncakeConnector | P → D | 简单轮询 |
| 分层版本 | MooncakeHybridConnector | D → P (按需) | 动态实例管理 |

### hosts/ports 参数

**计算规则**：
- hosts: 每节点 IP 重复 dp_size_local 次 (dp_size_local=2)
- ports: 7100 到 7100+dp_size_local-1 (7100, 7101)，每节点重复

**配置示例**：

```text
PREFILLER_HOSTS = 192.168.1.20 192.168.1.20 192.168.1.21 192.168.1.21 192.168.1.22 192.168.1.22 192.168.1.23 192.168.1.23
PREFILLER_PORTS = 7100 7101 7100 7101 7100 7101 7100 7101
DECODER_HOSTS = 192.168.1.30 192.168.1.30 192.168.1.31 192.168.1.31
DECODER_PORTS = 7100 7101 7100 7101
```

## Configuration Change Guide

### 需要手动修改的占位符

| 占位符 | 含义 | 替换为 |
|---|---|---|
| `<P1N1_IP>` | Prefill 实例1 节点1 IP | 实际 IP 地址 |
| `<P1N2_IP>` | Prefill 实例1 节点2 IP | 实际 IP 地址 |
| `<P2N1_IP>` | Prefill 实例2 节点1 IP | 实际 IP 地址 |
| `<P2N2_IP>` | Prefill 实例2 节点2 IP | 实际 IP 地址 |
| `<D1N1_IP>` | Decode 实例1 节点1 IP | 实际 IP 地址 |
| `<D1N2_IP>` | Decode 实例1 节点2 IP | 实际 IP 地址 |
| `<PROXY_IP>` | 代理服务 IP | 实际代理服务器 IP |

### 本示例配置 IP 映射

| 占位符 | 实际 IP |
|---|---|
| `<P1N1_IP>` | 192.168.1.20 |
| `<P1N2_IP>` | 192.168.1.21 |
| `<P2N1_IP>` | 192.168.1.22 |
| `<P2N2_IP>` | 192.168.1.23 |
| `<D1N1_IP>` | 192.168.1.30 |
| `<D1N2_IP>` | 192.168.1.31 |
| `<PROXY_IP>` | 192.168.1.40 |

## Testing and Validation

### 验证服务状态

```bash
# 检查 Prefill 服务
curl http://192.168.1.20:7100/health
curl http://192.168.1.21:7100/health
curl http://192.168.1.22:7100/health
curl http://192.168.1.23:7100/health

# 检查 Decode 服务
curl http://192.168.1.30:7100/health
curl http://192.168.1.31:7100/health

# 检查代理状态
curl http://192.168.1.40:1999/healthcheck
```

### 发送测试请求

```bash
curl -X POST http://192.168.1.40:1999/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/root/.cache/DeepSeek-V4-Pro",
    "prompt": "Hello, how are you?",
    "max_tokens": 50
  }'
```

## Directory Structure

```text
pd_disaggregation_deepseek_v4_pro_2p2n_1d2n/
├── sources/
│   ├── DeepSeek-V4-Pro.md
│   ├── pd_disaggregation_mooncake_multi_node.md
│   ├── launch_online_dp.py
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   ├── start_container.sh
│   ├── run_dp_template_prefill_node1.sh
│   ├── run_dp_template_prefill_node2.sh
│   ├── run_dp_template_decode_node1.sh
│   └── run_dp_template_decode_node2.sh
├── prefill/
│   ├── start_container.sh
│   ├── instance1/
│   │   ├── node1/
│   │   │   ├── launch_online_dp.py
│   │   │   ├── run_dp_template.sh
│   │   │   └── start_serve.sh
│   │   └── node2/
│   │       ├── launch_online_dp.py
│   │       ├── run_dp_template.sh
│   │       └── start_serve.sh
│   └── instance2/
│       ├── node1/
│       │   ├── launch_online_dp.py
│       │   ├── run_dp_template.sh
│       │   └── start_serve.sh
│       └── node2/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
├── decode/
│   ├── start_container.sh
│   └── instance1/
│       ├── node1/
│       │   ├── launch_online_dp.py
│       │   ├── run_dp_template.sh
│       │   └── start_serve.sh
│       └── node2/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
├── proxy/
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_proxy.sh
└── README.md
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | 2026-05-26 | model_name=DeepSeek-V4-Pro, version=0.18.0, machine_type=A3, prefill_instances=2, decode_instances=1, nodes_per_prefill=2, nodes_per_decode=2, proxy_type=分层版本 |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-26 | DeepSeek-V4-Pro.md 从 releases/v0.18.0 分支下载 |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-26 | Prefill-Decode Disaggregation 章节存在 |
| 4. 下载文件 | ✅ 完成 | 2026-05-26 | launch_online_dp.py, load_balance_proxy_server_example.py, load_balance_proxy_layerwise_server_example.py, pd_disaggregation_mooncake_multi_node.md |
| 5. 提取模板 | ✅ 完成 | 2026-05-26 | start_container.sh, run_dp_template_prefill_node1.sh, run_dp_template_prefill_node2.sh, run_dp_template_decode_node1.sh, run_dp_template_decode_node2.sh |
| 6. 生成部署树 | ✅ 完成 | 2026-05-26 | Prefill: 2实例×2节点 (P1N1, P1N2, P2N1, P2N2), Decode: 1实例×2节点 (D1N1, D1N2), Proxy: 分层版本 |
| 7. 验证一致性 | ✅ 完成 | 2026-05-26 | kv_role正确 (Prefill: kv_producer, Decode: kv_consumer), kv_port正确 (Prefill: 36000, Decode: 36200), engine_id正确 (P1: 1, P2: 3, D1: 2), kv_connector=MooncakeHybridConnector |
| 8. 编写 README | ✅ 完成 | 2026-05-26 | README.md 包含完整部署说明和工作流日志 |

**生成时间**：2026-05-26

## Node Configuration Summary

### Prefill Nodes

| 节点 | kv_role | kv_port | engine_id | dp_rank_start | local_ip |
|---|---|---|---|---|---|
| P1N1 | kv_producer | 36000 | 1 | 0 | 192.168.1.20 |
| P1N2 | kv_producer | 36000 | 1 | 2 | 192.168.1.21 |
| P2N1 | kv_producer | 36000 | 3 | 4 | 192.168.1.22 |
| P2N2 | kv_producer | 36000 | 3 | 6 | 192.168.1.23 |

### Decode Nodes

| 节点 | kv_role | kv_port | engine_id | dp_rank_start | local_ip |
|---|---|---|---|---|---|
| D1N1 | kv_consumer | 36200 | 2 | 0 | 192.168.1.30 |
| D1N2 | kv_consumer | 36200 | 2 | 2 | 192.168.1.31 |

### kv-transfer-config Summary

所有节点的 kv-transfer-config 包含：
- kv_connector: MooncakeHybridConnector
- prefill.dp_size: 8
- prefill.tp_size: 8
- decode.dp_size: 4
- decode.tp_size: 8
- --tensor-parallel-size: 8