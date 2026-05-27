# GLM5.1 PD分离部署包 (6P2N 4D2N)

## 概述

本部署包为 GLM5.1 模型的 Prefill-Decode 分离架构配置，采用 6 个 Prefill 实例（每实例 2 节点）+ 4 个 Decode 实例（每实例 2 节点）的部署方案。

**特殊配置说明**：GLM5 采用不同 Prefill/Decode 的 tp_size 配置：
- Prefill: tp_size=16, dp_size_local=1
- Decode: tp_size=4, dp_size_local=4

## 配置参数

| 参数 | 值 |
|------|-----|
| model_name | GLM5.1 |
| version | 0.18.0 |
| machine_type | A3 (Atlas 800 A3, 128G x 16) |
| model_path | /root/.cache/GLM5.1 |
| extra_mounts | /mnt |
| nic_name | eth0 |
| kv_connector | MooncakeConnectorV1 |
| proxy_type | 基础版本 |

### 并行参数

| 参数 | Prefill | Decode | 说明 |
|------|---------|--------|------|
| tp_size | 16 | 4 | Tensor Parallel Size |
| dp_size_local | 1 | 4 | 每节点 DP 进程数 |
| 总 dp_size | 12 | 32 | 实例×节点×dp_size_local |
| 总节点数 | 12 | 8 | 实例数×节点数 |

### Prefill 节点 IP 配置

| 实例 | 节点 | IP | kv_port | engine_id | dp_rank_start |
|------|------|-----|---------|-----------|---------------|
| 1 | 1 | 192.168.1.101 | 36000 | 1 | 0 |
| 1 | 2 | 192.168.1.102 | 36000 | 1 | 1 |
| 2 | 1 | 192.168.1.103 | 36100 | 2 | 0 |
| 2 | 2 | 192.168.1.104 | 36100 | 2 | 1 |
| 3 | 1 | 192.168.1.105 | 36200 | 3 | 0 |
| 3 | 2 | 192.168.1.106 | 36200 | 3 | 1 |
| 4 | 1 | 192.168.1.107 | 36300 | 4 | 0 |
| 4 | 2 | 192.168.1.108 | 36300 | 4 | 1 |
| 5 | 1 | 192.168.1.109 | 36400 | 5 | 0 |
| 5 | 2 | 192.168.1.110 | 36400 | 5 | 1 |
| 6 | 1 | 192.168.1.111 | 36500 | 6 | 0 |
| 6 | 2 | 192.168.1.112 | 36500 | 6 | 1 |

### Decode 节点 IP 配置

| 实例 | 节点 | IP | kv_port | engine_id | dp_rank_start |
|------|------|-----|---------|-----------|---------------|
| 1 | 1 | 192.168.2.101 | 36600 | 7 | 0 |
| 1 | 2 | 192.168.2.102 | 36600 | 7 | 4 |
| 2 | 1 | 192.168.2.103 | 36700 | 8 | 8 |
| 2 | 2 | 192.168.2.104 | 36700 | 8 | 12 |
| 3 | 1 | 192.168.2.105 | 36800 | 9 | 16 |
| 3 | 2 | 192.168.2.106 | 36800 | 9 | 20 |
| 4 | 1 | 192.168.2.107 | 36900 | 10 | 24 |
| 4 | 2 | 192.168.2.108 | 36900 | 10 | 28 |

| Proxy | - | 192.168.3.1 | 1999 | - | - |

## 目录结构

```
pd_disaggregation_glm5_1_6p2n_4d2n/
├── sources/                                    # 源模板文件
│   ├── GLM5.md                                 # 模型教程文档
│   ├── pd_disaggregation_mooncake_multi_node.md # PD分离理论参考
│   ├── start_container.sh                      # 容器启动脚本模板
│   ├── launch_online_dp.py                     # DP启动脚本
│   ├── run_dp_template_prefill_node*.sh        # Prefill节点模板
│   ├── run_dp_template_decode_node*.sh         # Decode节点模板
│   ├── load_balance_proxy_server_example.py    # 基础版本代理
│   └── load_balance_proxy_layerwise_server_example.py # 分层版本代理
├── prefill/                                    # Prefill部署目录
│   ├── start_container.sh                      # Prefill容器启动脚本
│   ├── instance1/node1/, node2/
│   ├── instance2/node1/, node2/
│   ├── instance3/node1/, node2/
│   ├── instance4/node1/, node2/
│   ├── instance5/node1/, node2/
│   └── instance6/node1/, node2/
├── decode/                                     # Decode部署目录
│   ├── start_container.sh                      # Decode容器启动脚本
│   ├── instance1/node1/, node2/
│   ├── instance2/node1/, node2/
│   ├── instance3/node1/, node2/
│   └── instance4/node1/, node2/
├── proxy/                                      # Proxy部署目录
│   ├── load_balance_proxy_server_example.py    # 基础版本代理
│   ├── load_balance_proxy_layerwise_server_example.py # 分层版本代理
│   └── start_proxy.sh                          # Proxy启动脚本
└── README.md                                   # 本文档
```

## 部署步骤

### 1. 启动容器

在每个节点上启动 Docker 容器：

**Prefill 节点（12个）：**
```bash
cd prefill
bash start_container.sh
```

**Decode 节点（8个）：**
```bash
cd decode
bash start_container.sh
```

### 2. 启动 Prefill 服务

按实例顺序启动 Prefill 节点：

```bash
# Instance 1
cd prefill/instance1/node1 && bash start_serve.sh  # 192.168.1.101
cd prefill/instance1/node2 && bash start_serve.sh  # 192.168.1.102

# Instance 2-6 同理...
```

### 3. 启动 Decode 服务

按实例顺序启动 Decode 节点：

```bash
# Instance 1
cd decode/instance1/node1 && bash start_serve.sh  # 192.168.2.101
cd decode/instance1/node2 && bash start_serve.sh  # 192.168.2.102

# Instance 2-4 同理...
```

### 4. 启动 Proxy 服务

在 Proxy 节点 (192.168.3.1) 上：

```bash
cd proxy
bash start_proxy.sh
```

### 5. 测试服务

通过 Proxy 发送请求：

```bash
curl http://192.168.3.1:1999/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "glm-5",
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

### hosts/ports 配置

**Prefill（dp_size_local=1）**：
- 12个节点，每节点1个端口
- PREFILLER_HOSTS: 192.168.1.101 ... 192.168.1.112（共12个）
- PREFILLER_PORTS: 7100（重复12次）

**Decode（dp_size_local=4）**：
- 8个节点，每节点4个端口（7100-7103）
- DECODER_HOSTS: 每节点IP重复4次（共32个）
- DECODER_PORTS: 7100 7101 7102 7103（重复8次）

## KV Transfer 配置

### Prefill 配置
```json
{
  "kv_connector": "MooncakeConnectorV1",
  "kv_role": "kv_producer",
  "kv_port": "36000",
  "engine_id": "1",
  "kv_connector_extra_config": {
    "use_ascend_direct": true,
    "prefill": {"dp_size": 12, "tp_size": 16},
    "decode": {"dp_size": 32, "tp_size": 4}
  }
}
```

### Decode 配置
```json
{
  "kv_connector": "MooncakeConnectorV1",
  "kv_role": "kv_consumer",
  "kv_port": "36600",
  "engine_id": "7",
  "kv_connector_extra_config": {
    "use_ascend_direct": true,
    "prefill": {"dp_size": 12, "tp_size": 16},
    "decode": {"dp_size": 32, "tp_size": 4}
  }
}
```

## GLM5 特殊配置说明

### 不同 tp_size 配置

GLM5 PD 分离采用不同的 Prefill/Decode tp_size：
- Prefill 使用 tp_size=16（全卡并行，减少通信开销）
- Decode 使用 tp_size=4（允许更多 DP 并行，提高吞吐）

### 200K Context Window

为了支持 200K 上下文窗口，Prefill 节点需要添加 `layer_sharding` 配置：
```json
"--additional-config": {"layer_sharding": ["q_b_proj"]}
```

注意：`layer_sharding` 仅在 Prefill 节点启用，Decode 节点不能启用。

## 工作流执行日志

| 步骤 | 状态 | 时间戳 | 摘要 |
|------|------|--------|------|
| 1. 收集参数 | ✅ 完成 | 2026-05-27 | 使用预定义参数，跳过交互式问答 |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-27 | GLM5.md (1398行) |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-27 | 找到 Prefill-Decode Disaggregation 章节 (行 639) |
| 4. 下载文件 | ✅ 完成 | 2026-05-27 | launch_online_dp.py, proxy 脚本 |
| 5. 提取模板 | ✅ 完成 | 2026-05-27 | GLM5 A3 格式，MooncakeConnectorV1 |
| 6. 生成部署树 | ✅ 完成 | 2026-05-27 | 6P×2N=12节点, 4D×2N=8节点 |
| 7. 验证一致性 | ✅ 完成 | 2026-05-27 | kv_port/engine_id 配置正确 |
| 8. 编写 README | ✅ 完成 | 2026-05-27 | 文档编写完成 |

**生成时间**：2026-05-27

### 详细执行记录

**步骤 1：收集参数**
- 使用预定义参数，跳过 AskUserQuestion
- 参数：model_name=GLM5.1, version=0.18.0, machine_type=A3
- 特殊配置：Prefill tp_size=16, Decode tp_size=4

**步骤 2：下载基础文件**
- URL: https://raw.githubusercontent.com/vllm-project/vllm-ascend/releases/v0.18.0/docs/source/tutorials/models/GLM5.md
- 文件大小：1398行

**步骤 3：检查部署模式支持**
- 章节标题：Prefill-Decode Disaggregation (行 639)
- 支持确认：模型支持 PD 分离部署

**步骤 4：下载文件**
- pd_disaggregation_mooncake_multi_node.md
- load_balance_proxy_server_example.py
- load_balance_proxy_layerwise_server_example.py
- launch_online_dp.py

**步骤 5：提取模板**
- 文档格式：GLM5 A3 格式
- kv_connector：MooncakeConnectorV1（不同于 DeepSeek 的 MooncakeHybridConnector）
- 特殊配置：Prefill tp_size=16, Decode tp_size=4

**步骤 6：生成部署树**
- Prefill：6 实例 × 2 节点 = 12 节点
- Decode：4 实例 × 2 节点 = 8 节点
- kv_port 配置：Prefill 36000-36500, Decode 36600-36900
- engine_id 配置：Prefill 1-6, Decode 7-10

**步骤 7：验证一致性**
- kv_role 检查：Prefill kv_producer ✓, Decode kv_consumer ✓
- kv_port 检查：P1=36000, P6=36500, D1=36600, D4=36900 ✓
- engine_id 检查：P1=1, P6=6, D1=7, D4=10 ✓
- dp_rank_start 检查：D1N1=0, D1N2=4, D4N2=28 ✓
- kv_connector 检查：MooncakeConnectorV1 ✓

## 参考

- [GLM5 模型教程](sources/GLM5.md)
- [PD分离理论参考](sources/pd_disaggregation_mooncake_multi_node.md)