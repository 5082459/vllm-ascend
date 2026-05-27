# 步骤 7：编写 README

## 目标

为生成的部署包编写 README.md 文档。

## 硬性规则

- 包含所有必需章节。
- 在「工作流执行日志」部分记录完整的执行过程。
- 提供清晰的启动顺序和配置修改指南。

## 必需章节

| 章节 | 必需内容 |
|---|---|
| Deployment Overview | 描述多节点部署架构 |
| Hardware and Software Requirements | 机型、卡数、节点数、前提条件 |
| Image Information | 镜像名称和来源 |
| Container Startup Instructions | 启动方法和参数说明 |
| Source File Origins | 获取时间戳、URL、版本信息 |
| Startup Sequence | 逐步启动顺序（必须先启动 Node 0） |
| Configuration Change Guide | 占位符值和修改说明 |
| Testing and Validation | 测试命令和验证方法 |
| Workflow Execution Log | 完整执行记录 |

## 章节内容模板

### Deployment Overview

```markdown
## Deployment Overview

**部署模式**：多节点部署

**架构说明**：多机分布式部署，Node 0 作为 Master 节点，其他节点作为 Worker。使用数据并行进行分布式推理。

**节点配置**：
- Node 0: Master 节点
- Node 1-N: Worker 节点
```

### Hardware and Software Requirements

```markdown
## Hardware and Software Requirements

**机型**：{machine_type}

**卡数**：{cards_per_node}

**节点数**：{node_count}

**前提条件**：
- vllm-ascend {version} 环境
- 模型权重已下载到 {model_path}
- 容器镜像已准备
- 各节点网络互通
```

### Startup Sequence

```markdown
## Startup Sequence

**重要**：必须先启动 Node 0，再启动其他节点。

1. 启动 Node 0（Master节点）
   cd node0
   ./start_container.sh
   ./run_serve.sh

2. 启动 Node 1（Worker节点）
   cd node1
   ./start_container.sh
   ./run_serve.sh

3. （如有更多节点）按顺序启动 Node 2、Node 3...
```

### Configuration Change Guide

```markdown
## Configuration Change Guide

### 配置说明

| 参数 | 说明 |
|---|---|
| {model_path} | 模型权重路径 |
| {nic_name} | 网络通信网卡名称 |

**注意**：所有节点的 `--data-parallel-address` 必须指向 Node 0 的 IP。
```

### Testing and Validation

```markdown
## Testing and Validation

### 基本测试

curl http://{node0_ip}:8000/v1/models

### 推理测试

curl http://{node0_ip}:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "{model_name}", "prompt": "Hello", "max_tokens": 100}'
```

### Workflow Execution Log

```markdown
## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | {timestamp} | {summary} |
| 2. 下载基础文件 | ✅ 完成 | {timestamp} | {summary} |
| 3. 检查部署模式支持 | ✅ 完成 | {timestamp} | {summary} |
| 4. 提取模板 | ✅ 完成 | {timestamp} | {summary} |
| 5. 生成部署树 | ✅ 完成 | {timestamp} | {summary} |
| 6. 验证一致性 | ✅ 完成 | {timestamp} | {summary} |
| 7. 编写 README | ✅ 完成 | {timestamp} | {summary} |

**生成时间**：{generation_timestamp}
```

## 日志条目格式

每个步骤的摘要应包含：

- 步骤 1：收集的参数列表、parallel_config_mode 值、当自定义配置时的 dp_size_local 和 dp_size_total
- 步骤 2：下载的文件列表
- 步骤 3：支持检查结果
- 步骤 4：提取的脚本列表
- 步骤 5：生成的目录结构、parallel_config_mode 值、当自定义配置时各节点的 dp_rank_start 值
- 步骤 6：验证检查项和结果、parallel_config_mode 相关验证说明
- 步骤 7：README 编写完成