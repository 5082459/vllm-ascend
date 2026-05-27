# 步骤 1：收集部署参数

## 目标

收集 PD 分离部署所需参数。

## 硬性规则

- 仅使用本文件列出的示例值。
- **如果所有参数已通过场景文件或 prompt 预定义，直接使用这些参数，跳过 AskUserQuestion**
- **检测预定义参数：如果 prompt 或场景文件中包含完整的参数表（含所有必需参数），视为预定义模式**
- 使用 `request_user_input` 工具，一次 1-4 个问题。
- `header` 必须 12 个字符以内。
- `options` 必须包含 2-3 个互斥选项。
- 第一个选项必须是推荐项，label 要带 "(Recommended)"。
- 不要手动加 "Other" 选项，客户端会自动补自由输入项。
- 在 README 的「工作流执行日志」部分记录步骤 1 摘要。

## 预定义参数检测规则

当检测到以下条件时，跳过 AskUserQuestion，直接使用预定义参数：

1. **检测标记**：prompt 包含「所有参数已在下方参数表中预定义」或「跳过所有 AskUserQuestion」
2. **参数表存在**：存在 Markdown 表格，包含 `参数 | 测试值` 或类似格式
3. **参数完整性**：表格包含所有必需参数：
   - model_name, version, machine_type, model_path, extra_mounts, nic_name
   - prefill_instances, decode_instances, nodes_per_prefill_instance, nodes_per_decode_instance
   - proxy_type
   - 所有 Prefill IP（prefill_p{P}_n{N}_ip）、Decode IP（decode_d{D}_n{N}_ip）、Proxy IP（proxy_ip）

当检测到预定义模式时：
- 直接从参数表读取值
- 不调用 AskUserQuestion
- 记录「步骤 1：使用预定义参数，跳过交互式问答」到日志

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

### 第一批问题

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

### 第二批问题

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
      "id": "nodes_per_prefill",
      "question": "请选择每个 Prefill 实例中的机器数量",
      "options": [
        {"label": "1 (Recommended)", "description": "每个 Prefill 实例使用 1 台机器"},
        {"label": "2", "description": "每个 Prefill 实例使用 2 台机器"}
      ]
    },
    {
      "header": "D节点数",
      "id": "nodes_per_decode",
      "question": "请选择每个 Decode 实例中的机器数量",
      "options": [
        {"label": "1 (Recommended)", "description": "每个 Decode 实例使用 1 台机器"},
        {"label": "2", "description": "每个 Decode 实例使用 2 台机器"}
      ]
    }
  ]
}
```

### 第三批问题

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

### 第四批问题（节点 IP 地址）

**Prefill 节点 IP：**

```json
{
  "questions": [
    {
      "header": "P1N1 IP",
      "id": "prefill_p1_n1_ip",
      "question": "请输入 Prefill 实例1 节点1 的 IP 地址",
      "options": [
        {"label": "192.168.1.1 (Recommended)", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.1.1", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    },
    {
      "header": "P1N2 IP",
      "id": "prefill_p1_n2_ip",
      "question": "请输入 Prefill 实例1 节点2 的 IP 地址（如有）",
      "options": [
        {"label": "192.168.1.2 (Recommended)", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.1.2", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    }
  ]
}
```

> 注：根据 `prefill_instances × nodes_per_prefill` 数量，动态生成对应数量的 IP 问题。

**Decode 节点 IP：**

```json
{
  "questions": [
    {
      "header": "D1N1 IP",
      "id": "decode_d1_n1_ip",
      "question": "请输入 Decode 实例1 节点1 的 IP 地址",
      "options": [
        {"label": "192.168.2.1 (Recommended)", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.2.1", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    },
    {
      "header": "D1N2 IP",
      "id": "decode_d1_n2_ip",
      "question": "请输入 Decode 实例1 节点2 的 IP 地址（如有）",
      "options": [
        {"label": "192.168.2.2 (Recommended)", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.2.2", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    }
  ]
}
```

> 注：根据 `decode_instances × nodes_per_decode` 数量，动态生成对应数量的 IP 问题。

**Proxy 节点 IP：**

```json
{
  "questions": [
    {
      "header": "Proxy IP",
      "id": "proxy_ip",
      "question": "请输入 Proxy 服务的 IP 地址",
      "options": [
        {"label": "192.168.3.1 (Recommended)", "description": "示例 IP，请通过 Other 输入实际 IP"},
        {"label": "10.0.3.1", "description": "示例 IP，请通过 Other 输入实际 IP"}
      ]
    }
  ]
}
```

## 参数映射

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
| nodes_per_prefill | nodes_per_prefill_instance | 每个 Prefill 实例的节点数 |
| nodes_per_decode | nodes_per_decode_instance | 每个 Decode 实例的节点数 |
| proxy_type | proxy_type | 代理类型 |
| prefill_p{P}_n{N}_ip | prefill_ips | Prefill 实例P节点N的IP地址（动态生成） |
| decode_d{D}_n{N}_ip | decode_ips | Decode 实例D节点N的IP地址（动态生成） |
| proxy_ip | proxy_ip | Proxy 服务IP地址 |

## IP 参数命名规则

IP 参数 ID 格式：
- Prefill：`prefill_p{实例号}_n{节点号}_ip`（如 `prefill_p1_n1_ip`）
- Decode：`decode_d{实例号}_n{节点号}_ip`（如 `decode_d1_n1_ip`）
- Proxy：`proxy_ip`

**动态生成逻辑**：
- 根据 `prefill_instances × nodes_per_prefill_instance` 计算 Prefill IP 问题数量
- 根据 `decode_instances × nodes_per_decode_instance` 计算 Decode IP 问题数量
- 每次最多收集 4 个 IP（AskUserQuestion 限制）

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

## 代理类型映射

| proxy_type | 代理脚本 | kv_connector |
|---|---|---|
| 基础版本 | load_balance_proxy_server_example.py | MooncakeConnector |
| 分层版本 | load_balance_proxy_layerwise_server_example.py | MooncakeLayerwiseConnector |

## PD 分离参数计算公式

```text
# tp_size 从模板中获取，保持原值不变

dp_size_local = 单机卡数 / tp_size  # tp_size 为模板中的值

prefill_dp_size = prefill_instances × nodes_per_prefill_instance × dp_size_local
decode_dp_size = decode_instances × nodes_per_decode_instance × dp_size_local

prefill_kv_port = 36000 + instance_index × 100
decode_kv_port = 与对应 Prefill 实例相同或继续递增

prefill_engine_id = 1, 2, 3... (按实例递增)
decode_engine_id = prefill_count + 1, prefill_count + 2... (继续递增)
```

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
- 计算后的 dp_size_local、prefill_dp_size、decode_dp_size
- 用户输入的任何自由格式值