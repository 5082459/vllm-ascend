# DeepSeek-V3.1 Multi-node Deployment

## Deployment Overview

**部署模式**：多节点部署 (Multi-node Deployment)

**架构说明**：多机分布式部署，Node 0 作为 Master 节点，Node 1 作为 Worker 节点。使用数据并行进行分布式推理。

**节点配置**：
- Node 0: Master 节点，负责接收请求和协调推理
- Node 1: Worker 节点，通过 `--headless` 模式连接 Master 节点

## Hardware and Software Requirements

**机型**：A3 超节点 (Atlas 900 A3)

**卡数**：每节点 16 卡

**节点数**：2

**前提条件**：
- vllm-ascend latest 版本环境（main 分支）
- 模型权重已下载到 `/root/.cache/DeepSeek-V3.1`
- 容器镜像已准备：`m.daocloud.io/quay.io/ascend/vllm-ascend:latest`
- 各节点网络互通，使用 `eth0` 网卡通信

## Image Information

**镜像名称**：`m.daocloud.io/quay.io/ascend/vllm-ascend:latest`

**镜像来源**：vllm-ascend 官方镜像仓库

## Parallel Configuration

| 参数 | 值 | 说明 |
|---|---|---|
| `--data-parallel-size` | 4 | 总数据并行大小 (dp_size_local × node_count) |
| `--data-parallel-size-local` | 2 | 单节点数据并行大小 (16卡 / tp_size) |
| `--tensor-parallel-size` | 8 | 张量并行大小 |
| `--enable-expert-parallel` | 启用 | 专家并行（MoE 模型） |

**计算公式**：
- dp_size_local = 单机卡数 / tp_size = 16 / 8 = 2
- dp_size_total = dp_size_local × node_count = 2 × 2 = 4

## Container Startup Instructions

每个节点需要启动 Docker 容器，容器内运行 vllm serve 服务。

**容器挂载目录**：
- `/root/.cache/DeepSeek-V3.1` - 模型权重路径
- `/mnt` - 额外挂载目录

**设备映射**：
- A3 机型：映射 16 个 NPU 设备 (`/dev/davinci[0-15]`)

## Source File Origins

| 文件 | URL | 获取时间 |
|---|---|---|
| DeepSeek-V3.1.md | https://raw.githubusercontent.com/vllm-project/vllm-ascend/main/docs/source/tutorials/models/DeepSeek-V3.1.md | 2026-05-26 |

**版本信息**：
- vllm-ascend 版本：latest (main 分支)
- 模型：DeepSeek-V3.1

## Startup Sequence

**重要**：必须先启动 Node 0，再启动 Node 1。

### 1. 启动 Node 0（Master 节点）

```bash
cd node0
./start_container.sh
# 容器启动后，在容器内执行
./run_serve.sh
```

### 2. 启动 Node 1（Worker 节点）

```bash
cd node1
./start_container.sh
# 容器启动后，在容器内执行
# 注意：先修改 run_serve.sh 中的 local_ip 为 Node 1 的实际 IP
./run_serve.sh
```

## Configuration Change Guide

### 必须修改的配置

| 参数 | 当前值 | 说明 |
|---|---|---|
| `local_ip` (Node 0) | `192.168.1.10` | Node 0 的实际 IP 地址 |
| `local_ip` (Node 1) | `<NODE1_IP>` | 需替换为 Node 1 的实际 IP |
| `node0_ip` | `192.168.1.10` | Master 节点 IP，所有节点必须指向此地址 |
| `nic_name` | `eth0` | 网络通信网卡名称 |

### 容器配置修改

| 参数 | 说明 |
|---|---|---|
| `IMAGE` | Docker 镜像版本，根据环境调整 |
| `/root/.cache/DeepSeek-V3.1` | 模型权重路径 |

**注意**：
- 所有节点的 `--data-parallel-address` 必须指向 Node 0 的 IP 地址
- Node 1 必须包含 `--headless` 参数
- Node 1 的 `--data-parallel-start-rank` = 2

## Testing and Validation

### 基本测试

```bash
curl http://192.168.1.10:8004/v1/models
```

### 推理测试

```bash
curl http://192.168.1.10:8004/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek_v3",
    "prompt": "Hello, how are you?",
    "max_tokens": 100
  }'
```

### 验证多节点通信

检查 Node 0 和 Node 1 的 HCCL 连接状态，确保数据并行通信正常。

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | 完成 | 2026-05-26 | model=DeepSeek-V3.1, version=latest, machine=A3, node_count=2, dp_size=2, tp_size=8 |
| 2. 下载基础文件 | 完成 | 2026-05-26 | 下载 DeepSeek-V3.1.md 到 sources 目录 |
| 3. 检查部署模式支持 | 完成 | 2026-05-26 | 找到 Multi-node Deployment 章节（第140行） |
| 4. 提取模板 | 完成 | 2026-05-26 | 提取 start_container.sh, run_node0.sh, run_node1.sh |
| 5. 生成部署树 | 完成 | 2026-05-26 | 生成 node0/node1 目录，DP=4, DP_local=2, TP=8 |
| 6. 验证一致性 | 完成 | 2026-05-26 | 文件结构完整，参数配置正确 |
| 7. 编写 README | 完成 | 2026-05-26 | README.md 编写完成 |

**生成时间**：2026-05-26

## Directory Structure

```
multi_node_deepseek_v3_1_2nodes/
├── sources/
│   ├── DeepSeek-V3.1.md          # 模型教程文档
│   ├── start_container.sh        # 容器启动脚本模板
│   ├── run_node0.sh              # Node 0 启动脚本模板
│   └── run_node1.sh              # Node 1 启动脚本模板
├── node0/
│   ├── start_container.sh        # Node 0 容器启动脚本
│   └── run_serve.sh              # Node 0 服务启动脚本
├── node1/
│   ├── start_container.sh        # Node 1 容器启动脚本
│   └── run_serve.sh              # Node 1 服务启动脚本
└── README.md                     # 部署说明文档
```