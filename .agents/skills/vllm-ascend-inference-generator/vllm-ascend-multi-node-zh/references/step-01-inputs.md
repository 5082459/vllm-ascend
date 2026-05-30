# 步骤 1：收集部署参数

## 目标

通过 AskUserQuestion 把多节点部署所需的全部参数一次性收集齐，作为步骤 2-6 的输入。

## 关键规则

- 一次提问 1-4 个问题，`header` ≤ 12 字符，options 2-3 个互斥项。
- 每组的第一个 option 是推荐项，label 末尾带 ` (Recommended)`。
- 不要手动加 "Other"——客户端会自动补一个自由输入入口。
- IP 类问题（`node{N}_ip`）的 options 都是**示例**，引导用户走 Other 输入实际 IP；不要在 label 上加 "(Recommended)"，避免误导用户直接选示例 IP。

## 第零批：模型、版本与镜像

```json
{
  "questions": [
    {
      "header": "模型名称",
      "id": "model_name",
      "question": "请选择待部署的模型名称",
      "options": [
        {"label": "Qwen2.5-72B (Recommended)", "description": "Qwen2.5 72B，适合多节点"},
        {"label": "DeepSeek-V3", "description": "DeepSeek V3"},
        {"label": "Llama3-70B", "description": "Llama3 70B"}
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
    },
    {
      "header": "镜像来源",
      "id": "image_source",
      "question": "请选择容器镜像来源",
      "options": [
        {"label": "使用模板镜像 (Recommended)", "description": "沿用教程模板里的镜像，仅按 version 替换 |vllm_ascend_version| 占位符"},
        {"label": "自定义镜像", "description": "用户提供完整镜像字符串，整体替换模板里的 IMAGE 行"}
      ]
    }
  ]
}
```

> 版本到 GitHub 分支/tag 的映射见 [SKILL.md「版本映射」](../SKILL.md#版本映射共享)。

仅当 `image_source = "自定义镜像"`，再补一问拿到完整镜像字符串：

```json
{
  "questions": [
    {
      "header": "自定义镜像",
      "id": "custom_image",
      "question": "请输入完整镜像字符串（含 registry/repo:tag）",
      "options": [
        {"label": "quay.io/ascend/vllm-ascend:custom-tag（示例）", "description": "示例值，请通过 Other 输入实际镜像"},
        {"label": "my-registry.internal/vllm-ascend:0.18.0-a3（示例）", "description": "示例值，请通过 Other 输入实际镜像"}
      ]
    }
  ]
}
```

> `image_source = "使用模板镜像"` 时跳过此追问；`custom_image` 在 step-04 整行替换 `start_container.sh` 中的 `IMAGE=...`。

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
        {"label": "A2", "description": "Atlas 800 A2,8 卡/机"}
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
      "header": "网卡名称",
      "id": "nic_name",
      "question": "请选择用于多节点通信的网卡名称",
      "options": [
        {"label": "eth0 (Recommended)", "description": "单网卡环境"},
        {"label": "bond0", "description": "多网卡聚合环境"}
      ]
    },
    {
      "header": "节点数",
      "id": "node_count",
      "question": "请选择部署节点数量",
      "options": [
        {"label": "2 (Recommended)", "description": "2 节点"},
        {"label": "4", "description": "4 节点"}
      ]
    }
  ]
}
```

## 第二批：挂载与并行模式

```json
{
  "questions": [
    {
      "header": "挂载目录",
      "id": "extra_mounts",
      "question": "是否需要在容器中挂载额外目录",
      "options": [
        {"label": "/mnt (Recommended)", "description": "挂载 /mnt"},
        {"label": "无额外挂载", "description": "仅挂载模型路径"}
      ]
    },
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
        {"label": "自动计算 (Recommended)", "description": "DP_local = 单机卡数 / TP，总 DP = DP_local × 节点数"},
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

> 并行参数的应用规则见 [SKILL.md「并行参数策略」](../SKILL.md#并行参数策略)。具体的 `dp_size_local` / `dp_size_total` / 各节点 `dp_rank_start` 由 step-04 调用 `scripts/compute_multi_node_params.py` 一次性算出，不要在这里手算。

## 第四批：节点 IP

按 `node_count` 数量逐个收集，options 只是示例，引导用户走 Other 输入实际 IP：

```json
{
  "questions": [
    {
      "header": "Node0 IP",
      "id": "node0_ip",
      "question": "请输入 Node 0（Master）的 IP 地址",
      "options": [
        {"label": "192.168.1.1（示例）", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.1.1（示例）", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    },
    {
      "header": "Node1 IP",
      "id": "node1_ip",
      "question": "请输入 Node 1 的 IP 地址",
      "options": [
        {"label": "192.168.1.2（示例）", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.1.2（示例）", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    }
  ]
}
```

> 一次最多 4 个问题，`node_count > 4` 时分批问。Master 必须是 `node0`。

## 参数映射

| id | 含义 | 何时收集 |
|---|---|---|
| model_name / version | 模型与版本 | 必收 |
| image_source | 镜像来源（模板/自定义） | 必收 |
| custom_image | 自定义镜像完整字符串 | 仅 image_source=自定义镜像 |
| machine_type | 硬件平台 | 必收 |
| model_path / extra_mounts | 路径配置 | 必收 |
| nic_name | 多节点通信网卡 | 必收 |
| node_count | 节点数量 | 必收 |
| parallel_config_mode | 并行配置方式 | 必收 |
| dp_size / tp_size / enable_ep | 并行参数 | 仅自定义 |
| node{N}_ip | 各节点 IP | 必收（按 node_count） |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 收集到的参数摘要（模型、版本、机型、节点数、IP 列表）
- `parallel_config_mode` 取值
