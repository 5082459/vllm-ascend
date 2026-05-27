# GLM-4.7 Multi-node Deployment

## Deployment Overview

**部署模式**：多节点部署

**架构说明**：多机分布式部署，Node 0 作为 Master 节点，其他节点作为 Worker。使用数据并行进行分布式推理。

**节点配置**：
- Node 0: Master 节点，接收请求并协调推理
- Node 1: Worker 节点，参与分布式推理计算

## Hardware and Software Requirements

**机型**：A3 超节点 (Atlas 900 A3)

**卡数**：16 卡/节点

**节点数**：2

**前提条件**：
- vllm-ascend latest 环境
- 模型权重已下载到 `/root/.cache/GLM-4.7`
- 容器镜像已准备：`quay.io/ascend/vllm-ascend:latest-a3`
- 各节点网络互通，网卡名称为 `eth0`
- 已验证多节点通信环境

## Image Information

**镜像名称**：`quay.io/ascend/vllm-ascend:latest-a3`

**镜像来源**：华为 Ascend 官方镜像仓库

## Container Startup Instructions

启动容器脚本挂载以下关键目录：
- `/root/.cache/GLM-4.7` → `/root/.cache` (模型权重)
- `/mnt` → `/mnt` (额外挂载目录)
- 16 个 NPU 设备 (`/dev/davinci[0-15]`)

## Source File Origins

**获取时间戳**：2026-05-23

**来源 URL**：https://raw.githubusercontent.com/vllm-project/vllm-ascend/main/docs/source/tutorials/models/GLM4.md

**版本信息**：latest (main branch)

**提取章节**：Multi-node Deployment

## Startup Sequence

**重要**：必须先启动 Node 0 (Master 节点)，再启动 Node 1 (Worker 节点)。

### 1. 启动 Node 0 (Master 节点)

```bash
cd node0
./start_container.sh
./run_serve.sh
```

### 2. 启动 Node 1 (Worker 节点)

```bash
cd node1
./start_container.sh
./run_serve.sh
```

## Configuration Change Guide

### 需要手动修改的占位符

| 占位符 | 含义 | 替换为 |
|---|---|---|
| `<NODE0_IP>` | Node 0 IP | Master 节点实际 IP 地址 |
| `<NODE1_IP>` | Node 1 IP | Worker 节点实际 IP 地址 |
| `eth0` | 网卡名称 | 实际网卡名称（如有不同） |

### 修改方法

使用文本编辑器打开对应的脚本文件，替换占位符值。

**注意**：
- 所有节点的 `--data-parallel-address` 必须指向 Node 0 的 IP
- Node 0 的 `local_ip` 和 `node0_ip` 应为相同值

### 关键参数说明

| 参数 | 值 | 说明 |
|---|---|---|
| `--tensor-parallel-size` | 2 | 张量并行大小 |
| `--data-parallel-size` | 16 | 总数据并行大小 (dp_size_local × node_count) |
| `--data-parallel-size-local` | 8 | 本节点数据并行大小 (单机卡数/tp_size) |
| `--data-parallel-start-rank` | Node0: 0, Node1: 8 | 数据并行起始 rank |
| `--data-parallel-rpc-port` | 13389 | 数据并行 RPC 端口 |
| `--headless` | Node1 有，Node0 无 | Worker 节点需要 headless 参数 |
| `--enable-expert-parallel` | 存在 | 启用专家并行（MoE 模型） |
| `--speculative-config` | mtp 配置 | 推测解码配置 |
| `--served-model-name` | glm47 | 服务模型名称 |

## Testing and Validation

### 基本测试

```bash
curl http://<NODE0_IP>:8004/v1/models
```

### 推理测试

```bash
curl http://<NODE0_IP>:8004/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "glm47", "prompt": "Hello", "max_tokens": 100}'
```

### Chat Completion 测试

```bash
curl http://<NODE0_IP>:8004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "glm47", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}'
```

## Directory Structure

```text
multi_node_glm4_7_2nodes/
├── sources/
│   ├── GLM4.md     # 模型教程文档
│   ├── start_container.sh   # 容器启动脚本源文件
│   ├── run_node0.sh         # Node 0 启动脚本源文件
│   └── run_node1.sh         # Node 1 启动脚本源文件
├── node0/
│   ├── start_container.sh   # Node 0 容器启动脚本
│   └── run_serve.sh         # Node 0 服务启动脚本 (Master)
├── node1/
│   ├── start_container.sh   # Node 1 容器启动脚本
│   └── run_serve.sh         # Node 1 服务启动脚本 (Worker)
└── README.md                # 部署说明文档
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | 2026-05-23 | model_name=GLM-4.7, version=latest, machine_type=A3, node_count=2, tp_size=2, dp_size_local=8, dp_size_total=16 |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-23 | 使用 baseline 源文件：GLM4.md, start_container.sh, run_node0.sh, run_node1.sh |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-23 | Multi-node Deployment 章节存在，支持多节点部署 |
| 4. 提取模板 | ✅ 完成 | 2026-05-23 | 提取容器脚本和 Node 0/1 启动脚本 |
| 5. 生成部署树 | ✅ 完成 | 2026-05-23 | 生成 node0, node1 目录，各含 2 个脚本文件 |
| 6. 验证一致性 | ✅ 完成 | 2026-05-23 | Node0 无 headless, Node1 有 headless; dp_rank_start: Node0=0, Node1=8; dp_size=16 一致 |
| 7. 编写 README | ✅ 完成 | 2026-05-23 | README.md 包含完整部署说明和日志 |

**生成时间**：2026-05-23

## Notes

### MoE 模型参数

GLM-4.7 是 MoE 模型，部署时需要额外参数：
- `--enable-expert-parallel`：启用专家并行
- `--speculative-config`：推测解码配置，使用 mtp 方法
- `--enable_shared_expert_dp`：启用共享专家数据并行

### served-model-name

GLM-4.7 的 served-model-name 设置为 `glm47`，与 reasoning-parser 和 tool-call-parser 配置一致。