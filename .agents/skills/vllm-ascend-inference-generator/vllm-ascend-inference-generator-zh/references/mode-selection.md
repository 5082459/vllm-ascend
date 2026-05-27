# 模式选择

## 目标

收集部署模式参数，然后调用对应的子技能。

## 硬性规则

- 仅收集部署模式参数，模型名称和版本由子技能收集。
- 使用 `request_user_input` 工具，一次 1-4 个问题。
- `header` 必须 12 个字符以内。
- `options` 必须包含 2-3 个互斥选项。
- 第一个选项必须是推荐项，label 要带 "(Recommended)"。
- 不要手动加 "Other" 选项，客户端会自动补自由输入项。

## request_user_input 调用

```json
{
  "questions": [
    {
      "header": "部署模式",
      "id": "deployment_mode",
      "question": "请选择部署模式",
      "options": [
        {"label": "单节点部署 (Recommended)", "description": "单机部署，适用于快速验证和低延迟场景"},
        {"label": "多节点部署", "description": "多机分布式部署，适用于大模型和高吞吐场景"},
        {"label": "PD分离部署", "description": "Prefill-Decode分离，适用于高并发场景"}
      ]
    }
  ]
}
```

## 参数映射

| id | 参数名 | 含义 |
|---|---|---|
| deployment_mode | deployment_mode | 部署模式 |

## 下一步

收集完参数后，根据 deployment_mode 使用 Skill 工具调用对应的子技能：

| deployment_mode | 子技能名称 | Skill 调用参数 |
|---|---|---|
| single-node | vllm-ascend-single-node-zh | `skill: "vllm-ascend-single-node-zh"` |
| multi-node | vllm-ascend-multi-node-zh | `skill: "vllm-ascend-multi-node-zh"` |
| pd-disaggregation | vllm-ascend-pd-disaggregation-zh | `skill: "vllm-ascend-pd-disaggregation-zh"` |

子技能内部完成模型名称、版本和其他部署参数的收集。