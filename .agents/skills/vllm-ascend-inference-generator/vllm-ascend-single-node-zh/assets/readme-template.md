<!-- 模板使用说明（最终 README 中应删除此注释块）：
     - {xxx} 形式占位符由 step-06-readme.md 替换为实际值
     - 渲染完成后此注释块需要被删除
-->
# 单节点 vllm-ascend 部署包

## Deployment Overview

**部署模式**：单节点部署

**架构说明**：单机部署 `{model_name}`，通过数据并行 + 张量并行运行推理服务。

**并行配置方式**：{parallel_config_mode}

## Hardware and Software Requirements

| 项 | 值 |
|---|---|
| 机型 | {machine_type} |
| 单机卡数 | {cards_per_node} |
| vllm-ascend 版本 | {version} |
| 模型路径 | {model_path} |
| 额外挂载 | {extra_mounts} |

**前提条件**：
- 已准备 vllm-ascend {version} 容器镜像
- 模型权重已下载到 `{model_path}`
- 节点已正确安装 NPU 驱动

## Image Information

镜像信息从模型教程的 Installation 章节提取，详见 `node/start_container.sh`。

## Container Startup

```bash
cd node
./start_container.sh
```

## Source File Origins

| 文件 | 来源 |
|---|---|
| `sources/{model_name}.md` | GitHub vllm-project/vllm-ascend `{version_tag}` 分支 |
| `sources/start_container.sh` | 教程 Environment Preparation 章节 |
| `sources/run_single_node.sh` | 教程 Single-node Deployment 章节 |

## Startup Sequence

```text
1. 启动容器：
   cd node
   ./start_container.sh

2. 进入容器后启动服务：
   ./run_serve.sh
```

## Configuration Change Guide

部署前需要把以下占位符替换为实际值：

| 占位符 | 含义 | 替换为 |
|---|---|---|
| `<LOCAL_IP>` | 本节点 IP | 节点的实际 IP 地址 |

并行配置说明：
- 当前配置模式：**{parallel_config_mode}**
- DP / TP / EP：{dp_size} / {tp_size} / {enable_ep}（"模板默认"表示沿用教程模板）

## Testing and Validation

启动完成后：

```bash
# 列出已加载模型
curl http://<LOCAL_IP>:8000/v1/models

# 推理测试
curl http://<LOCAL_IP>:8000/v1/completions \
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
