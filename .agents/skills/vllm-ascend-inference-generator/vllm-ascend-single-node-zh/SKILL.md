---
name: vllm-ascend-single-node-zh
description: 单节点 vllm-ascend 推理服务部署脚本生成。【重要约束】每次调用必须是全新流程，从零开始，禁止继承或应用之前的任何经验或资料，仅使用本次skill调用范围内的references目录信息。
---

# 单节点部署技能

为 vllm-ascend 生成单机部署包：一个容器启动脚本 + 一个 vllm serve 启动脚本。适用于快速验证和低延迟场景。

## 信息边界

每次调用都是独立流程。本次执行允许使用的信息源**只有三类**：

1. 本次会话中读取的 `references/`、`assets/` 目录文件
2. 用户在本次请求中提供的参数（包括 prompt、场景文件、AskUserQuestion 回答）
3. 通过 `curl` 实时拉取的 GitHub 官方教程文档

之所以强调这一点：模型教程会随版本演化，模板里的 DP/TP 默认值也可能调整。任何"凭印象"得到的参数都可能与用户指定的版本不一致——宁可重新读、重新拉、重新算。

## 使用场景

- **可独立调用**：用户明确请求单节点部署
- **可由主技能调用**：`vllm-ascend-inference-generator-zh` 在模式选择阶段路由到本 skill

## 工作流

按顺序执行 6 个步骤。任一步骤失败立即触发[失败终止协议](#失败终止协议)。

| 步骤 | 文件 | 产出 | 下一步消费者 |
|---|---|---|---|
| 1. 收集参数 | [step-01-inputs.md](references/step-01-inputs.md) | 部署参数（模型、版本、机型、并行配置等） | step-02、step-04 |
| 2. 下载并校验支持 | [step-02-download-and-check.md](references/step-02-download-and-check.md) | `sources/{model_name}.md` + 章节存在性确认 | step-03 |
| 3. 提取模板 | [step-03-extract.md](references/step-03-extract.md) | `sources/start_container.sh`、`sources/run_single_node.sh` | step-04、step-05 |
| 4. 生成部署树 | [step-04-generate.md](references/step-04-generate.md) | `node/` 完整目录 | step-05、step-06 |
| 5. 验证一致性 | [step-05-validate.md](references/step-05-validate.md) | 验证报告（写入日志） | step-06 |
| 6. 编写 README | [step-06-readme.md](references/step-06-readme.md) | `README.md` | — |

辅助资源：
- README 模板：[assets/readme-template.md](assets/readme-template.md)

## 全局约定

下面的规则被多个步骤共享，集中放在这里以避免每个步骤再重复一次。

### 输出目录命名

格式：`single_node_{model_normalized}`

- `model_normalized`：把模型名转小写，再把 `-` 和 `.` 都替换成 `_`，去掉重复下划线

示例：`single_node_deepseek_v3_1`

> 该命名被现有测试基线锁定，**不要随意更改**。

### 失败终止协议

任一步骤检测到不可恢复错误时，按下面的顺序执行，不再进入后续步骤：

1. 向用户输出失败消息（步骤内会给出具体模板）
2. 停止读取后续 step 文件
3. 停止任何文件生成、拷贝、写入操作
4. 工作流终止，本次 skill 调用结束

之所以坚持"硬终止"而不是"尽力而为"：半成品部署包（缺占位符替换、参数不一致）对用户的危害大于"什么都没有"——他真去 run，会得到一堆隐蔽的运行时错误。

### 工作流执行日志

每个步骤完成时，向最终 `README.md` 的「Workflow Execution Log」表格追加一行，包含：状态、时间戳、关键产物或参数摘要。日志的最终渲染由 step-06 完成。

### 版本映射（共享）

| 用户输入 | GitHub 分支 | GitHub 标签 |
|---|---|---|
| latest | main | — |
| 0.18.0 | releases/v0.18.0 | v0.18.0 |
| 0.17.0 | releases/v0.17.0 | v0.17.0 |

优先使用 `releases/v{version}` 分支；分支不存在时回退到 `v{version}` 标签。

### 机型与卡数

| 机型 | 单机卡数 |
|---|---|
| A3 超节点（Atlas 900 A3） | 16 |
| A2（Atlas 800 A2） | 8 |

### 并行参数策略

- `parallel_config_mode = "使用模板配置"`：保留模板中的 DP/TP/EP，**不**重新计算（教程作者针对该机型 + 模型已挑过推荐切分）。
- `parallel_config_mode = "自定义并行配置"`：按 `dp_size_local = 单机卡数 / tp_size` 计算。当用户的 `dp_size` 选 "自动计算" 时使用该公式，否则取用户值。EP 仅当 `enable_ep = "启用"` 时附加 `--enable-expert-parallel`。

## 验证与回归

本 skill 已有完整测试基础设施位于 `tests/vllm-ascend-single-node-zh/`：

- `trigger/` — 触发测试
- `scenarios/*/baseline/` — 场景产出基线
- `runs/` — 历史运行记录
- 主入口工具：`tests/tools/run_test.py`

修改本 skill 后，至少跑一遍 `run_test.py` 与基线 diff，避免参数漂移。
