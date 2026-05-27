# DeepSeek-V3.1 单节点部署包

## Deployment Overview

**部署模式**：单节点部署

**架构说明**：单机部署，使用数据并行和张量并行进行推理服务。

## Hardware and Software Requirements

**机型**：A3 超节点 (Atlas 900 A3)

**卡数**：16

**前提条件**：
- vllm-ascend latest 环境
- 模型权重已下载到 /root/.cache/DeepSeek-V3.1
- 容器镜像已准备

## Image Information

**镜像名称**：m.daocloud.io/quay.io/ascend/vllm-ascend:latest

**镜像来源**：vllm-ascend 官方镜像

## Container Startup Instructions

### 启动容器

```bash
cd node
./start_container.sh
```

### 参数说明

- `--shm-size=512g`: 大模型需要更大共享内存
- `--device /dev/davinci[0-15]`: Atlas A3 16 卡设备
- `-v /root/.cache/DeepSeek-V3.1:/root/.cache/DeepSeek-V3.1`: 模型权重挂载
- `-v /mnt:/mnt`: 额外挂载目录

## Source File Origins

| 文件 | 来源 URL | 获取时间 |
|---|---|---|
| DeepSeek-V3.1.md | https://raw.githubusercontent.com/vllm-project/vllm-ascend/main/docs/source/tutorials/models/DeepSeek-V3.1.md | 2026-05-23 |
| start_container.sh | 从 Installation 章节提取 | 2026-05-23 |
| run_single_node.sh | 从 Single-node Deployment 章节提取 | 2026-05-23 |

## Startup Sequence

1. **启动容器**
   ```bash
   cd node
   ./start_container.sh
   ```

2. **启动服务**
   ```bash
   ./run_serve.sh
   ```

## Configuration Change Guide

### 需要手动修改的占位符

| 占位符 | 含义 | 替换为 |
|---|---|---|
| <LOCAL_IP> | 本节点 IP | 实际 IP 地址 |
| eth0 | 网卡名称 | 实际网卡名称 (通过 ifconfig 查看) |

### 修改方法

使用文本编辑器打开 `node/run_serve.sh`，替换占位符值：

```bash
# 修改网卡名称
nic_name="eth0"  # 替换为实际网卡名称

# 修改本地 IP
local_ip="<LOCAL_IP>"  # 替换为实际 IP 地址
```

## Testing and Validation

### 基本测试

```bash
curl http://{service_ip}:8015/v1/models
```

### 推理测试

```bash
curl http://{service_ip}:8015/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek_v3", "prompt": "Hello", "max_tokens": 100}'
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | 2026-05-23 | model_name=DeepSeek-V3.1, version=latest, machine_type=A3, model_path=/root/.cache/DeepSeek-V3.1, extra_mounts=/mnt, dp_size=4, tp_size=4 |
| 2. 下载基础文件 | ✅ 完成 | 2026-05-23 | 下载 DeepSeek-V3.1.md 模型教程 |
| 3. 检查部署模式支持 | ✅ 完成 | 2026-05-23 | 章节 "Single-node Deployment" 已找到 |
| 4. 提取模板 | ✅ 完成 | 2026-05-23 | 提取 start_container.sh, run_single_node.sh |
| 5. 生成部署树 | ✅ 完成 | 2026-05-23 | sources/: 3 文件, node/: 2 文件, dp_size=4, tp_size=4 |
| 6. 验证一致性 | ✅ 完成 | 2026-05-23 | 文件结构完整, 参数正确: dp=4, tp=4, <LOCAL_IP> 占位符存在 |
| 7. 编写 README | ✅ 完成 | 2026-05-23 | README.md 编写完成 |

**生成时间**：2026-05-23

**验证结果**：

| 检查项 | 结果 |
|---|---|
| vllm serve 命令完整性 | ✅ 包含完整参数 |
| --data-parallel-size | ✅ 4 |
| --tensor-parallel-size | ✅ 4 |
| --data-parallel-address | ✅ 不存在 (单节点不需要) |
| <LOCAL_IP> 占位符 | ✅ 存在 |