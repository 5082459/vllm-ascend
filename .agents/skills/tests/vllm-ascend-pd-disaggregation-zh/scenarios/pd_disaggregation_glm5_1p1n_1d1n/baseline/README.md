# GLM5 PD分离部署包 (1P1N 1D1N)

## Deployment Overview

**部署模式**：Prefill-Decode 分离部署

**架构说明**：Prefill 实例处理预填充阶段，Decode 实例处理解码阶段，代理负责负载均衡和 KV Cache 传输。

**配置**：
- Prefill 实例数：1
- Decode 实例数：1
- 每实例节点数：1

## Hardware and Software Requirements

| 项目 | 配置 |
|---|---|
| 机型 | Atlas 900 A3 (16卡) |
| 模型 | GLM5 |
| vllm-ascend 版本 | 0.18.0 |
| Prefill 实例 | 1实例 × 1节点 |
| Decode 实例 | 1实例 × 1节点 |

## Image Information

- 镜像名称：`quay.io/ascend/vllm-ascend:v0.18.0-a3`
- 镜像来源：vllm-ascend 官方镜像

## Container Startup Instructions

在每个节点上执行：
```bash
cd prefill/instance1/node1  # Prefill节点
./start_container.sh
./start_serve.sh

cd decode/instance1/node1  # Decode节点
./start_container.sh
./start_serve.sh
```

## Source File Origins

| 文件 | 来源 | 时间戳 |
|---|---|---|
| GLM5.md | vllm-ascend v0.18.0 docs | 2026-05-26 |
| launch_online_dp.py | vllm-ascend v0.18.0 examples | 2026-05-26 |
| load_balance_proxy_server_example.py | vllm-ascend v0.18.0 examples | 2026-05-26 |
| load_balance_proxy_layerwise_server_example.py | vllm-ascend v0.18.0 examples | 2026-05-26 |

## Startup Sequence

**重要**：必须按 Prefill → Decode → Proxy 顺序启动。

1. 启动 Prefill 实例节点
   ```bash
   cd prefill/instance1/node1
   ./start_container.sh
   ./start_serve.sh
   ```

2. 启动 Decode 实例节点
   ```bash
   cd decode/instance1/node1
   ./start_container.sh
   ./start_serve.sh
   ```

3. 启动代理
   ```bash
   cd proxy
   ./start_proxy.sh
   ```

## Proxy Configuration

### 代理类型选择

| 类型 | kv_connector | 路由方向 | 适用场景 |
|---|---|---|---|
| 基础版本 | MooncakeConnectorV1 | P → D | 简单轮询 |
| 分层版本 | MooncakeLayerwiseConnector | D → P（按需） | 动态实例管理 |

### hosts/ports 参数

**当前配置**：
- Prefill: 192.168.1.20, port 7100 (dp_size_local=1)
- Decode: 192.168.1.30, ports 7100-7103 (dp_size_local=4)

## Configuration Change Guide

### 需要手动修改的参数

| 参数 | 当前值 | 说明 |
|---|---|---|
| nic_name | eth0 | 网卡名称 |
| local_ip | Prefill: 192.168.1.20, Decode: 192.168.1.30 | 本机IP |
| model_path | /root/.cache/GLM5 | 模型权重路径 |

## Testing and Validation

```bash
curl http://192.168.1.40:1999/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "glm-5",
        "prompt": "The future of AI is",
        "max_completion_tokens": 50,
        "temperature": 0
    }'
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | 2026-05-26 | 模型: GLM5, 版本: 0.18.0, 机型: A3, 1P1N 1D1N |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-26 | GLM5.md 下载成功 |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-26 | 找到 Prefill-Decode Disaggregation 章节 |
| 4. 下载额外文件 | ✅ 完成 | 2026-05-26 | launch_online_dp.py, proxy scripts |
| 5. 提取模板 | ✅ 完成 | 2026-05-26 | prefill_node1.sh, decode_node1.sh |
| 6. 生成部署树 | ✅ 完成 | 2026-05-26 | prefill/decode/proxy 目录结构完整 |
| 7. 验证一致性 | ✅ 完成 | 2026-05-26 | kv_role, kv_port, engine_id 参数正确 |
| 8. 编写 README | ✅ 完成 | 2026-05-26 | README.md 生成完成 |

**生成时间**：2026-05-26

## 参数计算说明

### 参数来源

按照 GLM5 模型教程模板的实际配置生成：

| 参数 | Prefill | Decode |
|---|---|---|
| tp_size | 16 | 4 |
| dp_size_local | 1 (16/16) | 4 (16/4) |
| prefill_dp_size | 1 | - |
| decode_dp_size | - | 4 |

### KV 参数配置

| 节点 | kv_role | kv_port | engine_id | kv_connector |
|---|---|---|---|---|
| Prefill Node 1 | kv_producer | 36000 | 1 | MooncakeConnectorV1 |
| Decode Node 1 | kv_consumer | 36200 | 2 | MooncakeConnectorV1 |

### IP 配置

| 节点 | IP |
|---|---|
| Prefill Instance 1 Node 1 | 192.168.1.20 |
| Decode Instance 1 Node 1 | 192.168.1.30 |
| Proxy | 192.168.1.40 |

### kv_connector_extra_config 配置

```json
{
    "use_ascend_direct": true,
    "prefill": {
        "dp_size": 1,
        "tp_size": 16
    },
    "decode": {
        "dp_size": 4,
        "tp_size": 4
    }
}
```