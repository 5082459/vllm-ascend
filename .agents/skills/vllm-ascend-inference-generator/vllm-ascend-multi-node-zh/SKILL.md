---
name: vllm-ascend-multi-node-zh
description: 多节点 vllm-ascend 推理服务部署脚本生成。【重要约束】每次调用必须是全新流程，从零开始，禁止继承或应用之前的任何经验或资料，仅使用本次skill调用范围内的references目录信息。
---

# 多节点部署技能

为 vllm-ascend 生成跨节点的分布式部署包：node0 作 Master，其余节点作 Worker，通过数据并行协同推理。

## 信息边界

每次调用都是独立流程。本次执行允许使用的信息源**只有三类**：

1. 本次会话中读取的 `references/`、`scripts/`、`assets/` 目录文件
2. 用户在本次请求中提供的参数（包括 prompt、场景文件、AskUserQuestion 回答）
3. 通过 `curl` 实时拉取的 GitHub 官方教程文档

之所以强调这一点：模型教程、tp_size 默认值、节点排序方式都会随版本演化。任何"凭印象"得到的参数都可能与用户指定的版本不一致——宁可重新读、重新拉、重新算。

## 使用场景

- **可独立调用**：用户明确请求多节点部署
- **可由主技能调用**：`vllm-ascend-inference-generator-zh` 在模式选择阶段路由到本 skill

## 工作流

按顺序执行 6 个步骤。任一步骤失败立即触发[失败终止协议](#失败终止协议)。

| 步骤 | 文件 | 产出 | 下一步消费者 |
|---|---|---|---|
| 1. 收集参数 | [step-01-inputs.md](references/step-01-inputs.md) | 部署参数（模型、版本、机型、节点数、IP 等） | step-02、step-04 |
| 2. 下载并校验支持 | [step-02-download-and-check.md](references/step-02-download-and-check.md) | `sources/{model_name}.md` + 章节存在性确认 | step-03 |
| 3. 提取模板 | [step-03-extract.md](references/step-03-extract.md) | `sources/start_container.sh`、`sources/run_node*.sh` | step-04、step-05 |
| 4. 生成部署树 | [step-04-generate.md](references/step-04-generate.md) | `node{N}/` 完整目录 | step-05、step-06 |
| 5. 验证一致性 | [step-05-validate.md](references/step-05-validate.md) | 验证报告（写入日志） | step-06 |
| 6. 编写 README | [step-06-readme.md](references/step-06-readme.md) | `README.md` | — |

辅助资源：
- 参数确定性计算脚本：[scripts/compute_multi_node_params.py](scripts/compute_multi_node_params.py)
- README 模板：[assets/readme-template.md](assets/readme-template.md)

## 全局约定

下面的规则被多个步骤共享，集中放在这里以避免每个步骤再重复一次。

### 输出目录命名

格式：`multi_node_{model_normalized}_{N}nodes`

- `model_normalized`：把模型名转小写，再把 `-` 和 `.` 都替换成 `_`，去掉重复下划线
- `{N}` = 节点数量 (`node_count`)

示例：`multi_node_deepseek_v3_1_2nodes`

> 该命名被现有测试基线锁定，**不要随意更改**。

### 失败终止协议

任一步骤检测到不可恢复错误时，按下面的顺序执行，不再进入后续步骤：

1. 向用户输出失败消息（步骤内会给出具体模板）
2. 停止读取后续 step 文件
3. 停止任何文件生成、拷贝、写入操作
4. 工作流终止，本次 skill 调用结束

之所以坚持"硬终止"而不是"尽力而为"：多节点的脚本之间高度耦合（dp_rank_start、dp_size_local 必须按公式递增），半成品部署包对用户的危害大于"什么都没有"。

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
- `parallel_config_mode = "自定义并行配置"`：用 [`scripts/compute_multi_node_params.py`](scripts/compute_multi_node_params.py) 一次算出每个节点的 `dp_size_local`、`dp_size_total`、`dp_rank_start`，不要在生成过程中临时算。

## 验证与回归

本 skill 已有完整测试基础设施位于 `tests/vllm-ascend-multi-node-zh/`：

- `trigger/` — 触发测试
- `scenarios/*/baseline/` — 场景产出基线
- `runs/` — 历史运行记录
- 主入口工具：`tests/tools/run_test.py`

修改本 skill 后，至少跑一遍 `run_test.py` 与基线 diff，避免参数漂移。
