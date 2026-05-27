# DeepSeek-V4-Pro PD分离部署包 (1P2N 1D2N)

## 概述

本部署包为 DeepSeek-V4-Pro 模型的 Prefill-Decode 分离架构配置，采用 1 个 Prefill 实例（每实例 2 节点）+ 1 个 Decode 实例（每实例 2 节点）的部署方案。

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
| prefill_dp_size | 4 | Prefill 总 DP (1x2x2) |
| decode_dp_size | 4 | Decode 总 DP (1x2x2) |

### 节点 IP 配置

| 角色 | 实例 | 节点 | IP | kv_port | engine_id | dp_rank_start |
|------|------|------|-----|---------|-----------|---------------|
| Prefill | 1 | 1 | 192.168.1.20 | 36000 | 1 | 0 |
| Prefill | 1 | 2 | 192.168.1.21 | 36000 | 1 | 2 |
| Decode | 1 | 1 | 192.168.1.30 | 36200 | 2 | 0 |
| Decode | 1 | 2 | 192.168.1.31 | 36200 | 2 | 2 |
| Proxy | - | - | 192.168.1.40 | 1999 | - | - |

## 目录结构

```
pd_disaggregation_deepseek_v4_pro_1p2n_1d2n/
├── sources/                                    # 源模板文件
│   ├── DeepSeek-V4-Pro.md                     # 模型教程文档
│   ├── pd_disaggregation_mooncake_multi_node.md # PD分离理论参考
│   ├── start_container.sh                     # 容器启动脚本模板
│   ├── launch_online_dp.py                    # DP启动脚本
│   ├── run_dp_template_prefill_node1.sh       # Prefill节点1模板
│   ├── run_dp_template_prefill_node2.sh       # Prefill节点2模板
│   ├── run_dp_template_decode_node1.sh        # Decode节点1模板
│   ├── run_dp_template_decode_node2.sh        # Decode节点2模板
│   ├── load_balance_proxy_server_example.py   # 基础版本代理
│   └── load_balance_proxy_layerwise_server_example.py # 分层版本代理
├── prefill/                                    # Prefill部署目录
│   ├── start_container.sh                     # Prefill容器启动脚本
│   └── instance1/
│       ├── node1/
│       │   ├── launch_online_dp.py            # DP启动脚本
│       │   ├── run_dp_template.sh             # 运行模板脚本
│       │   └── start_serve.sh                 # 启动服务脚本
│       └── node2/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
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

# 在 192.168.1.21 (P1N2) 上执行
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

**P1N2 (192.168.1.21):**
```bash
cd instance1/node2
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
| PREFILLER_HOSTS | 192.168.1.20 192.168.1.20 192.168.1.21 192.168.1.21 |
| PREFILLER_PORTS | 7100 7101 7100 7101 |
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
    "prefill": {"dp_size": 4, "tp_size": 8},
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
    "prefill": {"dp_size": 4, "tp_size": 8},
    "decode": {"dp_size": 4, "tp_size": 8}
  }
}
```

## 工作流执行日志

### 步骤 1：收集参数
- 状态：完成
- 收集参数：model_name, version, machine_type, model_path, extra_mounts, nic_name, prefill_instances, decode_instances, nodes_per_prefill_instance, nodes_per_decode_instance, proxy_type, IP 配置

### 步骤 2：下载基础文件
- 状态：完成
- 下载文件：DeepSeek-V4-Pro.md, pd_disaggregation_mooncake_multi_node.md

### 步骤 3：检查部署模式支持
- 状态：完成
- 模型支持 PD 分离部署

### 步骤 4：下载文件
- 状态：完成
- 下载文件：launch_online_dp.py, load_balance_proxy_server_example.py, load_balance_proxy_layerwise_server_example.py

### 步骤 5：提取模板
- 状态：完成
- 文档格式：新格式（有 A2/A3 区分）
- 提取脚本：
  - sources/start_container.sh (A3 Installation 章节)
  - sources/run_dp_template_prefill_node1.sh (Prefill node 0)
  - sources/run_dp_template_prefill_node2.sh (Prefill node 1)
  - sources/run_dp_template_decode_node1.sh (Decode node)
  - sources/run_dp_template_decode_node2.sh (Decode node 复制)

### 步骤 6：生成部署树
- 状态：完成
- 目录结构：
  - prefill/instance1/node1, node2
  - decode/instance1/node1, node2
  - proxy/
- 关键参数：
  - tp_size: 8
  - dp_size_local: 2
  - prefill_dp_size: 4
  - decode_dp_size: 4
  - Prefill kv_port: 36000
  - Decode kv_port: 36200
  - Prefill engine_id: 1
  - Decode engine_id: 2

### 步骤 7：验证一致性
- 状态：完成
- 所有文件生成正确

### 步骤 8：编写 README
- 状态：完成
- 文档包含完整的部署说明和配置信息

## 参考

- [DeepSeek-V4-Pro 模型教程](sources/DeepSeek-V4-Pro.md)
- [PD分离理论参考](sources/pd_disaggregation_mooncake_multi_node.md)