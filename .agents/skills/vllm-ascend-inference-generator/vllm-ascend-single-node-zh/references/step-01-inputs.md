# 步骤 1：收集部署参数

## 目标

收集单节点部署所需参数。

## 硬性规则

- 仅使用本文件列出的示例值。
- 使用 `request_user_input` 工具，一次 1-4 个问题。
- `header` 必须 12 个字符以内。
- `options` 必须包含 2-3 个互斥选项。
- 第一个选项必须是推荐项，label 要带 "(Recommended)"。
- 不要手动加 "Other" 选项，客户端会自动补自由输入项。
- 在 README 的「工作流执行日志」部分记录步骤 1 摘要。

## 参数收集

### 第零批问题（模型和版本）

```json
{
  "questions": [
    {
      "header": "模型名称",
      "id": "model_name",
      "question": "请选择待部署的模型名称",
      "options": [
        {"label": "Qwen2.5-7B (Recommended)", "description": "Qwen2.5 7B 模型，适合单节点部署"},
        {"label": "Qwen2.5-14B", "description": "Qwen2.5 14B 模型，适合单节点部署"},
        {"label": "Llama3-8B", "description": "Llama3 8B 模型，适合单节点部署"}
      ]
    },
    {
      "header": "版本",
      "id": "version",
      "question": "请选择 vllm-ascend 框架版本",
      "options": [
        {"label": "latest (Recommended)", "description": "最新版本，映射到 main 分支"},
        {"label": "0.18.0", "description": "稳定版本 0.18.0"},
        {"label": "0.17.0", "description": "稳定版本 0.17.0"}
      ]
    }
  ]
}
```

### 第一批问题（基础配置）

```json
{
  "questions": [
    {
      "header": "机型",
      "id": "machine_type",
      "question": "请选择硬件平台类型",
      "options": [
        {"label": "A3超节点 (Recommended)", "description": "Atlas 900 A3 超节点，单机 16 卡"},
        {"label": "A2", "description": "Atlas 800 A2，单机 8 卡"}
      ]
    },
    {
      "header": "模型路径",
      "id": "model_path",
      "question": "请输入模型权重存储路径",
      "options": [
        {"label": "默认路径 (Recommended)", "description": "使用 /root/.cache/{model_name}，自动替换模型名"},
        {"label": "标准路径", "description": "使用 /data/models/{model_name}，自动替换模型名"}
      ]
    },
    {
      "header": "挂载目录",
      "id": "extra_mounts",
      "question": "是否需要在容器中挂载额外目录",
      "options": [
        {"label": "/mnt (Recommended)", "description": "挂载 /mnt 目录，常用于临时数据"},
        {"label": "无额外挂载", "description": "仅挂载模型路径"}
      ]
    }
  ]
}
```

### 第二批问题（并行配置方式）

```json
{
  "questions": [
    {
      "header": "并行配置",
      "id": "parallel_config_mode",
      "question": "请选择并行配置方式",
      "options": [
        {"label": "使用模板配置 (Recommended)", "description": "使用官网模板脚本中的 DP/TP/EP 配置，不做修改"},
        {"label": "自定义并行配置", "description": "手动配置 DP/TP/EP 参数"}
      ]
    }
  ]
}
```

### 第三批问题（仅当 parallel_config_mode=自定义并行配置 时执行）

**当选择"自定义并行配置"时，继续收集 DP/TP/EP 参数：**

```json
{
  "questions": [
    {
      "header": "DP大小",
      "id": "dp_size",
      "question": "请选择数据并行大小",
      "options": [
        {"label": "自动计算 (Recommended)", "description": "根据机型卡数和 TP 自动计算 DP = 卡数/TP"},
        {"label": "2", "description": "DP=2, 最小配置"},
        {"label": "4", "description": "DP=4, 标准配置"},
        {"label": "8", "description": "DP=8, 高吞吐配置"}
      ]
    },
    {
      "header": "TP大小",
      "id": "tp_size",
      "question": "请选择张量并行大小",
      "options": [
        {"label": "8 (Recommended)", "description": "TP=8, 标准配置"},
        {"label": "4", "description": "TP=4, 低资源配置"},
        {"label": "16", "description": "TP=16, 大模型配置"}
      ]
    },
    {
      "header": "EP开关",
      "id": "enable_ep",
      "question": "是否启用专家并行（仅 MoE 模型）",
      "options": [
        {"label": "不启用 (Recommended)", "description": "不使用专家并行，非 MoE 模型推荐"},
        {"label": "启用", "description": "启用专家并行，仅适用于 MoE 模型"}
      ]
    }
  ]
}
```

**当选择"使用模板配置"时**：
- 直接使用模板脚本中的 DP/TP/EP 配置
- 不询问 DP/TP/EP 参数
- 在生成脚本时保持模板参数不变

## 参数映射

| id | 参数名 | 含义 |
|---|---|---|
| model_name | model_name | 模型名称 |
| version | version | vllm-ascend 版本 |
| machine_type | machine_type | 硬件平台 |
| model_path | model_path | 模型权重路径 |
| extra_mounts | extra_mounts | 额外挂载目录 |
| parallel_config_mode | parallel_config_mode | 并行配置方式（模板配置/自定义配置） |
| dp_size | dp_size | 数据并行大小（仅自定义配置时收集） |
| tp_size | tp_size | 张量并行大小（仅自定义配置时收集） |
| ep_size | ep_size | 专家并行大小（仅自定义配置时收集） |

## 并行配置逻辑

**当 parallel_config_mode = "使用模板配置" 时**：
- 不收集 DP/TP/EP 参数
- 直接使用模板脚本中的配置
- 生成脚本时保持模板参数不变

**当 parallel_config_mode = "自定义并行配置" 时**：
- 收集 DP/TP/EP 参数
- 根据用户选择生成自定义配置
- DP 选择"自动计算"时：`dp_size = 卡数 / tp_size`

## 机型说明

| 机型 | 卡数 |
|---|---|
| A3 超节点（Atlas 900 A3） | 16 |
| A2（Atlas 800 A2） | 8 |

**卡数计算**：
- A3 超节点：固定 16 卡
- A2：固定 8 卡

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 收集的参数摘要
- 用户输入的任何自由格式值

## 版本映射

将 `{version_tag}` 替换为映射的分支或标签，优先尝试 release 分支，再是 tag：

| 用户输入 | GitHub 分支 | GitHub 标签 |
|---|---|---|
| latest | main | - |
| 0.18.0 | releases/v0.18.0 | v0.18.0 |
| 0.17.0 | releases/v0.17.0 | v0.17.0 |

**选择优先级**：

1. 优先尝试 `releases/v{version}` 分支。
2. 如果分支不存在，使用 `v{version}` 标签。