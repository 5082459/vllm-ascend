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

# 测试用例：单节点部署

## 测试场景

生成 DeepSeek-V3.1 单节点推理服务部署包。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | single-node |
| model_name | DeepSeek-V3.1 |
| version | latest |
| machine_type | A3 |
| model_path | /root/.cache/DeepSeek-V3.1 |
| extra_mounts | /mnt |
| dp_size | 4 |
| tp_size | 4 |

## 预期输出目录

```text
single_node_deepseek_v3_1/
├── sources/
│   ├── DeepSeek-V3.1.md
│   ├── start_container.sh
│   └── run_single_node.sh
├── node/
│   ├── start_container.sh
│   └── run_serve.sh
└── README.md
```

## 预期验证结果

| 检查项 | 预期结果 |
|---|---|
| vllm serve 命令完整性 | 包含完整参数 |
| --data-parallel-size | 4 |
| --tensor-parallel-size | 4 |
| 无 --data-parallel-address | 不存在 |
| <LOCAL_IP> 占位符 | 存在 |

## 测试执行步骤

1. 执行主技能，选择「单节点部署」
2. 调用 single-node 子技能
3. 验证生成的目录结构
4. 验证脚本参数正确性

## 测试通过标准

- 目录结构完整
- 所有脚本文件存在
- 参数替换正确
- README 包含工作流执行日志
