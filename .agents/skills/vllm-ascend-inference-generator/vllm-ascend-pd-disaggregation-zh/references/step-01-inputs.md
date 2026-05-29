# 步骤 1：收集部署参数

## 目标

收集 PD 分离部署所需的全部参数，写入工作流执行日志。

## 关键规则

- 仅使用本文件列出的示例值；用户可通过 "Other" 自由输入。
- **预定义模式优先**：如果 prompt / 场景文件已经把所有必需参数列齐，直接读取，不要再调用 AskUserQuestion。
- 使用 `request_user_input` 工具，每次问 1-4 个问题。
- `header` 不超过 12 字符，`options` 给 2-3 个互斥选项；第一项是推荐项，label 末尾加 `(Recommended)`。
- 不要手动添加 "Other"，工具会自动补。
- IP 类参数没有"推荐示例"——示例 IP 不带 `(Recommended)` 标签，避免用户误选。

## 预定义参数检测

如果以下三条全部满足，则跳过 AskUserQuestion，直接从 prompt 或场景文件提取参数：

1. prompt 里出现「所有参数已在下方参数表中预定义」或「跳过所有 AskUserQuestion」之类的标记
2. 存在 `参数 | 测试值` 形式的 Markdown 表格
3. 表格覆盖所有必需参数：
   - `model_name`、`version`、`machine_type`、`model_path`、`extra_mounts`、`nic_name`
   - `prefill_instances`、`decode_instances`、`nodes_per_prefill_instance`、`nodes_per_decode_instance`
   - `proxy_type`
   - 全部 Prefill IP（`prefill_p{P}_n{N}_ip`）、Decode IP（`decode_d{D}_n{N}_ip`）、`proxy_ip`

命中预定义模式时，在日志记录「步骤 1：使用预定义参数，跳过交互式问答」。

## 参数收集

### 第零批：模型与版本

```json
{
  "questions": [
    {
      "header": "模型名称",
      "id": "model_name",
      "question": "请选择待部署的模型名称",
      "options": [
        {"label": "DeepSeek-V3.1 (Recommended)", "description": "DeepSeek V3.1 模型，支持 PD 分离"},
        {"label": "DeepSeek-V4-Pro", "description": "DeepSeek V4 Pro 模型，支持 PD 分离"},
        {"label": "GLM5", "description": "GLM5 模型，支持 PD 分离"}
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

### 第一批：硬件与挂载

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
        {"label": "默认路径 (Recommended)", "description": "/root/.cache/{model_name}，自动替换模型名"},
        {"label": "标准路径", "description": "/data/models/{model_name}，自动替换模型名"}
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
    },
    {
      "header": "网卡名称",
      "id": "nic_name",
      "question": "请选择用于多节点通信的网卡名称",
      "options": [
        {"label": "eth0 (Recommended)", "description": "单网卡环境下的物理网卡"},
        {"label": "bond0", "description": "多网卡聚合环境下的绑定网卡"}
      ]
    }
  ]
}
```

### 第二批：实例与节点规模

```json
{
  "questions": [
    {
      "header": "Prefill数",
      "id": "prefill_instances",
      "question": "请选择 Prefill 实例数量",
      "options": [
        {"label": "1 (Recommended)", "description": "1 个 Prefill 实例"},
        {"label": "2", "description": "2 个 Prefill 实例"},
        {"label": "4", "description": "4 个 Prefill 实例"}
      ]
    },
    {
      "header": "Decode数",
      "id": "decode_instances",
      "question": "请选择 Decode 实例数量",
      "options": [
        {"label": "1 (Recommended)", "description": "1 个 Decode 实例"},
        {"label": "2", "description": "2 个 Decode 实例"},
        {"label": "4", "description": "4 个 Decode 实例"}
      ]
    },
    {
      "header": "P节点数",
      "id": "nodes_per_prefill_instance",
      "question": "请选择每个 Prefill 实例中的机器数量",
      "options": [
        {"label": "1 (Recommended)", "description": "每个 Prefill 实例使用 1 台机器"},
        {"label": "2", "description": "每个 Prefill 实例使用 2 台机器"}
      ]
    },
    {
      "header": "D节点数",
      "id": "nodes_per_decode_instance",
      "question": "请选择每个 Decode 实例中的机器数量",
      "options": [
        {"label": "1 (Recommended)", "description": "每个 Decode 实例使用 1 台机器"},
        {"label": "2", "description": "每个 Decode 实例使用 2 台机器"}
      ]
    }
  ]
}
```

### 第三批：代理类型

```json
{
  "questions": [
    {
      "header": "代理类型",
      "id": "proxy_type",
      "question": "请选择代理类型",
      "options": [
        {"label": "基础版本 (Recommended)", "description": "轮询负载均衡，适用于简单部署"},
        {"label": "分层版本", "description": "动态实例管理，适用于复杂部署"}
      ]
    }
  ]
}
```

### 第四批：节点 IP

> IP 没有"通用合理值"。所有候选项只是示例占位，不带 `(Recommended)` 标签——用户必须从 "Other" 输入实际 IP，否则后续生成的脚本无法在真实环境运行。
>
> 根据 `prefill_instances × nodes_per_prefill` 与 `decode_instances × nodes_per_decode` 动态生成对应数量的 IP 问题。AskUserQuestion 单批最多 4 个，超过时分多批问。

**Prefill 节点 IP 示例**：

```json
{
  "questions": [
    {
      "header": "P1N1 IP",
      "id": "prefill_p1_n1_ip",
      "question": "请输入 Prefill 实例1 节点1 的 IP 地址（请用 Other 输入实际 IP）",
      "options": [
        {"label": "192.168.1.1（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"},
        {"label": "10.0.1.1（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"}
      ]
    },
    {
      "header": "P1N2 IP",
      "id": "prefill_p1_n2_ip",
      "question": "请输入 Prefill 实例1 节点2 的 IP 地址（如有，请用 Other 输入实际 IP）",
      "options": [
        {"label": "192.168.1.2（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"},
        {"label": "10.0.1.2（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"}
      ]
    }
  ]
}
```

**Decode 节点 IP** 与 **Proxy IP** 同样按上述风格构造。Proxy 只需要 1 个：

```json
{
  "questions": [
    {
      "header": "Proxy IP",
      "id": "proxy_ip",
      "question": "请输入 Proxy 服务的 IP 地址（请用 Other 输入实际 IP）",
      "options": [
        {"label": "192.168.3.1（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"},
        {"label": "10.0.3.1（示例）", "description": "示例 IP，仅占位，请通过 Other 输入实际值"}
      ]
    }
  ]
}
```

## 参数映射表

| id | 参数名 | 含义 |
|---|---|---|
| model_name | model_name | 模型名称 |
| version | version | vllm-ascend 版本 |
| machine_type | machine_type | 硬件平台 |
| model_path | model_path | 模型权重路径 |
| extra_mounts | extra_mounts | 额外挂载目录 |
| nic_name | nic_name | 多节点通信网卡 |
| prefill_instances | prefill_instances | Prefill 实例数量 |
| decode_instances | decode_instances | Decode 实例数量 |
| nodes_per_prefill_instance | nodes_per_prefill_instance | 每 Prefill 实例的节点数 |
| nodes_per_decode_instance | nodes_per_decode_instance | 每 Decode 实例的节点数 |
| proxy_type | proxy_type | 代理类型 |
| prefill_p{P}_n{N}_ip | prefill_ips | Prefill 节点 IP（按实例×节点动态生成） |
| decode_d{D}_n{N}_ip | decode_ips | Decode 节点 IP（按实例×节点动态生成） |
| proxy_ip | proxy_ip | Proxy 服务 IP |

## IP 命名规则

- Prefill：`prefill_p{实例号}_n{节点号}_ip`，例如 `prefill_p1_n1_ip`
- Decode：`decode_d{实例号}_n{节点号}_ip`，例如 `decode_d1_n1_ip`
- Proxy：`proxy_ip`

## 共享映射

版本映射、代理类型映射在 [SKILL.md「全局约定」](../SKILL.md#全局约定) 一节统一定义，本步骤直接采用。

## 参数计算公式

详见 [appendix-pd-resources.md「PD分离参数计算公式」](appendix-pd-resources.md#pd分离参数计算公式)。计算工作在步骤 4 通过 `scripts/compute_pd_params.py` 完成，本步骤只需把 `tp_size` 从模板里读出来作为输入。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 参数摘要（哪些来自预定义、哪些来自交互回答）
- 用户在 "Other" 中提供的自由格式值
