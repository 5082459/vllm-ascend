# 步骤 1：收集部署参数

## 目标

通过 AskUserQuestion 把单节点部署所需的全部参数一次性收集齐，作为步骤 2-6 的输入。

## 关键规则

- 一次提问 1-4 个问题，`header` ≤ 12 字符，options 2-3 个互斥项。
- 每组的第一个 option 是推荐项，label 末尾带 ` (Recommended)`。
- 不要手动加 "Other"——客户端会自动补一个自由输入入口。

## 第零批：模型和版本

```json
{
  "questions": [
    {
      "header": "模型名称",
      "id": "model_name",
      "question": "请选择待部署的模型名称",
      "options": [
        {"label": "Qwen2.5-7B (Recommended)", "description": "Qwen2.5 7B，适合单节点"},
        {"label": "Qwen2.5-14B", "description": "Qwen2.5 14B"},
        {"label": "Llama3-8B", "description": "Llama3 8B"}
      ]
    },
    {
      "header": "版本",
      "id": "version",
      "question": "请选择 vllm-ascend 框架版本",
      "options": [
        {"label": "latest (Recommended)", "description": "main 分支"},
        {"label": "0.18.0", "description": "稳定版本"},
        {"label": "0.17.0", "description": "稳定版本"}
      ]
    }
  ]
}
```

> 版本到 GitHub 分支/tag 的映射见 [SKILL.md「版本映射」](../SKILL.md#版本映射共享)。

## 第一批：基础配置

```json
{
  "questions": [
    {
      "header": "机型",
      "id": "machine_type",
      "question": "请选择硬件平台类型",
      "options": [
        {"label": "A3超节点 (Recommended)", "description": "Atlas 900 A3，16 卡/机"},
        {"label": "A2", "description": "Atlas 800 A2，8 卡/机"}
      ]
    },
    {
      "header": "模型路径",
      "id": "model_path",
      "question": "请输入模型权重存储路径",
      "options": [
        {"label": "/root/.cache/{model_name} (Recommended)", "description": "自动替换模型名"},
        {"label": "/data/models/{model_name}", "description": "自动替换模型名"}
      ]
    },
    {
      "header": "挂载目录",
      "id": "extra_mounts",
      "question": "是否需要在容器中挂载额外目录",
      "options": [
        {"label": "/mnt (Recommended)", "description": "挂载 /mnt"},
        {"label": "无额外挂载", "description": "仅挂载模型路径"}
      ]
    }
  ]
}
```

## 第二批：并行配置方式

```json
{
  "questions": [
    {
      "header": "并行配置",
      "id": "parallel_config_mode",
      "question": "请选择并行配置方式",
      "options": [
        {"label": "使用模板配置 (Recommended)", "description": "沿用模板里的 DP/TP/EP，不修改"},
        {"label": "自定义并行配置", "description": "手动配置 DP/TP/EP"}
      ]
    }
  ]
}
```

## 第三批（仅当 parallel_config_mode=自定义并行配置）

```json
{
  "questions": [
    {
      "header": "DP大小",
      "id": "dp_size",
      "question": "请选择数据并行大小",
      "options": [
        {"label": "自动计算 (Recommended)", "description": "DP = 单机卡数 / TP"},
        {"label": "2", "description": "DP=2"},
        {"label": "4", "description": "DP=4"},
        {"label": "8", "description": "DP=8"}
      ]
    },
    {
      "header": "TP大小",
      "id": "tp_size",
      "question": "请选择张量并行大小",
      "options": [
        {"label": "8 (Recommended)", "description": "TP=8"},
        {"label": "4", "description": "TP=4"},
        {"label": "16", "description": "TP=16"}
      ]
    },
    {
      "header": "EP开关",
      "id": "enable_ep",
      "question": "是否启用专家并行（仅 MoE 模型）",
      "options": [
        {"label": "不启用 (Recommended)", "description": "非 MoE 模型推荐"},
        {"label": "启用", "description": "仅 MoE 模型"}
      ]
    }
  ]
}
```

> 并行参数的应用规则见 [SKILL.md「并行参数策略」](../SKILL.md#并行参数策略)。

## 参数映射

| id | 含义 | 何时收集 |
|---|---|---|
| model_name | 模型名称 | 必收 |
| version | vllm-ascend 版本 | 必收 |
| machine_type | 硬件平台 | 必收 |
| model_path | 模型权重路径 | 必收 |
| extra_mounts | 额外挂载目录 | 必收 |
| parallel_config_mode | 并行配置方式 | 必收 |
| dp_size | 数据并行大小 | 仅自定义 |
| tp_size | 张量并行大小 | 仅自定义 |
| enable_ep | 专家并行开关 | 仅自定义 |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 收集到的参数摘要
- `parallel_config_mode` 的取值
