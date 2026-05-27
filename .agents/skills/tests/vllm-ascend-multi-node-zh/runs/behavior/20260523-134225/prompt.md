You are running an automated behavior validation scenario.

Follow these rules exactly:
- Treat the scenario below as authoritative test input.
- Treat every value in the scenario's parameter table as already provided by the user.
- Map those parameter values directly to the skill's expected inputs and execute with them.
- Do not ask the user clarifying questions.
- Do not use brainstorming, writing-plans, or other meta-planning skills.
- This is not a design exercise. It is an execution-only validation run.
- Prefer directly invoking the most specific deployment skill implied by the scenario.
- If the scenario includes parameter tables or expected output names, use them directly.
- Complete the applicable skill workflow end-to-end in the current workspace.
- If you find a mismatch between scenario wording and upstream source content, continue with the actual source content and mention the discrepancy in your final response instead of asking a question.

Scenario:

# 测试用例：多节点部署 - Qwen2.5（缺失部署章节）

## 测试场景

测试当模型教程文档缺失「Multi-node Deployment」章节时，skill 应立即停止，不应生成部署目录。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | multi-node |
| model_name | Qwen2.5-72B |
| version | latest |
| machine_type | A3 |
| model_path | /root/.cache/Qwen2.5-72B |
| nic_name | eth0 |
| extra_mounts | /mnt |
| node_count | 2 |
| dp_size | 1 |
| tp_size | 8 |

## 文档状态

源文档 `Qwen2.5.md`（实际为 Qwen3-Dense 教程）：
- 不包含 `Multi-node Deployment` 章节
- 仅在 Environment Preparation 中有 `Verify Multi-node Communication(Optional)` 条目
- 实际部署章节为 `Online Inference on Multi-NPU`（单机多卡）和 `Offline Inference on Multi-NPU`

## 预期行为

Skill 应在步骤 3「检查部署模式支持」时：
- 检测到文档缺失 `Multi-node Deployment` 章节
- 立即停止流程
- 输出错误信息：「模型教程缺失 Multi-node Deployment 章节，无法生成部署包」

## 预期输出

**空输出**：不生成任何部署目录或脚本。

可能的输出：
- 无输出目录（skill 直接退出）
- 或仅生成空的 `sources/` 目录（仅下载源文件）

## 测试通过标准

- Skill 不生成 `node0/` 或 `node1/` 目录
- Skill 不生成 `run_serve.sh` 或 `start_container.sh` 脚本
- Skill 输出明确的错误信息说明停止原因
- README 不存在或为空（无部署说明）

## 边界验证目的

此测试验证 skill 的边界保护机制：
- 当源文档不支持请求的部署模式时，skill 必须立即停止
- 不能凭空生成不存在的部署脚本
- 不能使用其他章节（如 Online Inference）替代多节点部署
