<!-- 模板使用说明（最终 README 中应删除此注释块）：
     - {xxx} 形式占位符由 step-06-readme.md 替换为实际值
     - [[节循环 NODE_TABLE]]...[[结束 NODE_TABLE]] 段按节点展开
     - 渲染完成后此注释块需要被删除
-->
# 多节点 vllm-ascend 部署包

## Deployment Overview

**部署模式**：多节点部署

**架构说明**：跨节点分布式部署 `{model_name}`。Node 0 作为 Master，其余节点作为 Worker，通过数据并行协同完成推理。

**节点角色**：
- Node 0：Master 节点
- Node 1 ~ Node N：Worker 节点（启用 `--headless`）

**并行配置方式**：{parallel_config_mode}

## Hardware and Software Requirements

| 项 | 值 |
|---|---|
| 机型 | {machine_type} |
| 单机卡数 | {cards_per_node} |
| 节点数 | {node_count} |
| vllm-ascend 版本 | {version} |
| 模型路径 | {model_path} |
| 额外挂载 | {extra_mounts} |
| 通信网卡 | {nic_name} |

**前提条件**：
- 已准备 vllm-ascend {version} 容器镜像
- 模型权重已下载到 `{model_path}`
- 各节点网络互通且 NIC `{nic_name}` 可用

## Image Information

镜像信息从模型教程的 Installation 章节提取，详见各 `node{N}/start_container.sh`。

## Container Startup

每个节点上：

```bash
cd node{N}
./start_container.sh
```

## Source File Origins

| 文件 | 来源 |
|---|---|
| `sources/{model_name}.md` | GitHub vllm-project/vllm-ascend `{version_tag}` 分支 |
| `sources/start_container.sh` | 教程 Environment Preparation 章节 |
| `sources/run_node*.sh` | 教程 Multi-node Deployment 章节按节点提取 |

## Startup Sequence

**重要**：必须先启动 Node 0 (Master)，等服务建立后再启动其他节点。

```text
1. 启动 Node 0：
   ssh <node0>
   cd node0
   ./start_container.sh
   ./run_serve.sh

2. 启动 Node 1 (... 依次到 Node N-1)：
   ssh <nodeN>
   cd node{N}
   ./start_container.sh
   ./run_serve.sh
```

## Node Layout

[[节循环 NODE_TABLE]]
| node{N} | {node{N}_ip} | {dp_rank_start} | {headless_flag} |
[[结束 NODE_TABLE]]

> 表头：节点 / IP / dp_rank_start / headless

## Configuration Change Guide

部署前需要把以下占位符替换为实际值：

| 占位符 | 含义 | 替换为 |
|---|---|---|
| `<NODE0_IP>` | Master 节点 IP | Node 0 实际 IP |

并行配置说明：
- 当前模式：**{parallel_config_mode}**
- TP / DP_local / DP_total：{tp_size} / {dp_size_local} / {dp_size_total}
- EP：{enable_ep}（"模板默认"表示沿用教程模板）
- 各节点 `--data-parallel-start-rank` 已按 `N × DP_local` 递增写好，无需手改

## Testing and Validation

启动完成后，在 Master 节点：

```bash
# 列出已加载模型
curl http://<NODE0_IP>:8000/v1/models

# 推理测试
curl http://<NODE0_IP>:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "{model_name}", "prompt": "Hello", "max_tokens": 100}'
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ | {step1_timestamp} | {step1_summary} |
| 2. 下载并校验支持 | ✅ | {step2_timestamp} | {step2_summary} |
| 3. 提取模板 | ✅ | {step3_timestamp} | {step3_summary} |
| 4. 生成部署树 | ✅ | {step4_timestamp} | {step4_summary} |
| 5. 验证一致性 | ✅ | {step5_timestamp} | {step5_summary} |
| 6. 编写 README | ✅ | {step6_timestamp} | {step6_summary} |

**生成时间**：{generation_timestamp}
