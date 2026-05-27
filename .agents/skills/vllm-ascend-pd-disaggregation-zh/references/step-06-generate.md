# 步骤 6：生成部署树

## 目标

从 sources 目录拷贝脚本并生成 PD分离部署包结构。

## 前置条件

**必须先完成步骤 5**，确保以下文件存在于 `{output_dir}/sources/` 目录：

| 文件 | 必须 | 来源 |
|------|------|------|
| `{model_name}.md` | ✓ | 步骤 2 |
| `pd_disaggregation_mooncake_multi_node.md` | ✓ | 步骤 4 |
| `launch_online_dp.py` | ✓ | 步骤 4 |
| `start_container.sh` | ✓ | 步骤 5 |
| `run_dp_template_prefill_node*.sh` | ✓ | 步骤 5（至少1个） |
| `run_dp_template_decode_node*.sh` | ✓ | 步骤 5（至少1个） |
| `load_balance_proxy_server_example.py` | ✓ | 步骤 4 |
| `load_balance_proxy_layerwise_server_example.py` | ✓ | 步骤 4 |

**如果前置文件不存在，**执行终止流程**：

**终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-07-validate.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 步骤 6 前置条件未满足

缺少文件：{missing_file}
原因：步骤 5 未完成或执行失败
```

## 硬性规则

- 所有脚本先从 sources 目录拷贝，再做修改。
- 为每个 Prefill/Decode 实例节点生成独立的目录。
- 生成 proxy 目录和启动脚本。
- 在 README 的「工作流执行日志」部分记录步骤 6 摘要。

## 输出目录命名

格式：`pd_disaggregation_{model_normalized}_{P}p{Np}n_{D}d{Nd}n`

示例：
- `pd_disaggregation_deepseek_v4_pro_1p1n_1d1n`：1个Prefill实例(每实例1节点) + 1个Decode实例(每实例1节点)
- `pd_disaggregation_deepseek_v3_1_2p2n_1d1n`：2个Prefill实例(每实例2节点) + 1个Decode实例(每实例1节点)

**命名规则**：
- `{P}` = Prefill 实例数量
- `{Np}` = 每个Prefill实例的节点数 (nodes_per_prefill_instance)
- `{D}` = Decode 实例数量
- `{Nd}` = 每个Decode实例的节点数 (nodes_per_decode_instance)
- 例如：`1p1n_1d1n` 表示 1个Prefill实例×1节点 + 1个Decode实例×1节点

## 目录结构

```text
{output_dir}/
├── sources/
│   ├── {model_name}.md
│   ├── pd_disaggregation_mooncake_multi_node.html
│   ├── launch_online_dp.py
│   ├── run_dp_template_prefill_node*.sh
│   ├── run_dp_template_decode_node*.sh
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_container.sh
├── prefill/
│   ├── start_container.sh
│   └── instance{N}/node{M}/
│       ├── launch_online_dp.py
│       ├── run_dp_template.sh
│       └── start_serve.sh
├── decode/
│   ├── start_container.sh
│   └── instance{N}/node{M}/
│       ├── launch_online_dp.py
│       ├── run_dp_template.sh
│       └── start_serve.sh
├── proxy/
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_proxy.sh
└── README.md
```

## 参数计算公式

```text
# tp_size 从模板中获取，保持原值不变
dp_size_local = 单机卡数 / tp_size  # tp_size 为模板中的值

prefill_dp_size = prefill_instances × nodes_per_prefill_instance × dp_size_local
decode_dp_size = decode_instances × nodes_per_decode_instance × dp_size_local

# dp_rank_start：单个实例内按节点递增，各实例独立计算
dp_rank_start = (node_index - 1) × dp_size_local  # node_index 从 1 开始

# kv_port
prefill_kv_port = 36000 + instance_index × 100
decode_kv_port = 36000 + prefill_instances × 100 + instance_index × 100

# engine_id
prefill_engine_id = instance_index + 1  # 1, 2, 3...
decode_engine_id = prefill_instances + instance_index + 1
```

## kv_port 配置要求

| NPUs per Node | Recommended kv_port |
|---------------|---------------------|
| 8 (A2) | >= 28000 |
| 16 (A3) | >= 36000 |

推荐配置：
- Prefill instance 1: 36000
- Prefill instance 2: 36100
- Decode instance 1: 36200

## 生成步骤

### 步骤 1：拷贝容器脚本

- Prefill：`sources/start_container.sh` → `prefill/start_container.sh`
- Decode：`sources/start_container.sh` → `decode/start_container.sh`
- 修改点：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `{model_path}` | 用户提供的模型路径 | 模型权重目录 |
| `{extra_mounts}` | 用户提供的挂载目录 | 额外挂载 |

### 步骤 2：生成 PD 实例节点目录

遍历 Prefill 和 Decode 实例，为每个节点生成目录和脚本。Prefill 和 Decode 的生成逻辑相同，仅参数不同。

**遍历规则**：

| 角色 | 遍历范围 | 模板前缀 | kv_role | dp_size |
|------|----------|----------|---------|---------|
| Prefill | `prefill_instances × nodes_per_prefill_instance` | `run_dp_template_prefill_node` | `kv_producer` | prefill_dp_size |
| Decode | `decode_instances × nodes_per_decode_instance` | `run_dp_template_decode_node` | `kv_consumer` | decode_dp_size |

对每个实例 N 的每个节点 M，生成以下文件：

1. **拷贝 launch_online_dp.py**：
   - 来源：`sources/launch_online_dp.py`
   - 目标：`{role}/instance{N}/node{M}/launch_online_dp.py`
   - 修改：无（直接拷贝）

2. **拷贝 run_dp_template.sh**：

   **模板选择规则**：
   - 如果 `{M}` <= 教程模板数量：使用 `sources/run_dp_template_{role_prefix}_node{M}.sh`
   - 如果 `{M}` > 教程模板数量：使用 `sources/run_dp_template_{role_prefix}_node1.sh` 作为基础模板

   来源：按上述规则选择模板文件
   目标：`{role}/instance{N}/node{M}/run_dp_template.sh`
   - 修改点：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | 用户输入的当前节点 IP | 当前节点实际 IP |
| `kv_connector` | 按规则选择 | 见下方 `kv_connector` 替换规则 |
| `kv_role` | `kv_producer` / `kv_consumer` | Prefill 为 producer，Decode 为 consumer |
| `kv_port` | 按公式计算 | 见参数计算公式 |
| `engine_id` | 按公式计算 | 见参数计算公式 |
| `dp_size` (prefill) | prefill_dp_size | Prefill 实例总 DP |
| `dp_size` (decode) | decode_dp_size | Decode 实例总 DP |

**注意**：`tp_size` 保持模板原值不变，不做替换。

**`kv_connector` 替换规则**：

检查模板中的 `kv_connector` 值：
1. 如果模板中 `kv_connector` 为 `MooncakeConnector` 或 `MooncakeLayerwiseConnector`：
   - 根据用户选择的代理类型替换：
     - 基础版本代理 → `MooncakeConnector`
     - 分层版本代理 → `MooncakeLayerwiseConnector`
2. 如果模板中 `kv_connector` 为其他类型（如 `NpuConnector` 等）：
   - **保持模板原值不变**，不做替换

3. **生成 start_serve.sh**：

```bash
#!/bin/bash
python launch_online_dp.py \
    --dp-size {dp_size} \
    --tp-size {tp_size_from_template} \
    --dp-size-local {dp_size_local} \
    --dp-rank-start {dp_rank_start} \
    --dp-address {instance_first_node_ip} \
    --dp-rpc-port 12321 \
    --vllm-start-port 7100
```

**参数说明**：
- `{dp_size}`：Prefill 用 prefill_dp_size，Decode 用 decode_dp_size
- `{tp_size_from_template}` = 从模板脚本中提取的 tp_size 值
- `{dp_size_local}` = 单机卡数 / tp_size_from_template
- `{dp_rank_start}` = (node_index - 1) × dp_size_local（实例内按节点递增，各实例独立计算）
- `{instance_first_node_ip}` = 用户输入的当前实例首节点 IP（用于 DP 通信协调）

**dp_rank_start 计算示例**：

| 场景 | 实例 | 节点 | dp_size_local | dp_rank_start |
|------|------|------|---------------|---------------|
| 1p1n | P1 | N1 | 2 | 0 |
| 1p2n | P1 | N1 | 2 | 0 |
| 1p2n | P1 | N2 | 2 | 2 |
| 2p2n | P1 | N1 | 2 | 0 |
| 2p2n | P1 | N2 | 2 | 2 |
| 2p2n | P2 | N1 | 2 | 0 |
| 2p2n | P2 | N2 | 2 | 2 |
| 1d2n | D1 | N1 | 2 | 0 |
| 1d2n | D1 | N2 | 2 | 2 |

### 步骤 3：生成 Proxy 目录

1. **拷贝代理脚本**：
   - `sources/load_balance_proxy_server_example.py` → `proxy/load_balance_proxy_server_example.py`
   - `sources/load_balance_proxy_layerwise_server_example.py` → `proxy/load_balance_proxy_layerwise_server_example.py`

2. **生成 start_proxy.sh**：

```bash
#!/bin/bash
# Proxy startup script

PROXY_TYPE="{proxy_type}"  # "basic" or "layerwise"
PROXY_PORT="1999"
PROXY_HOST="{proxy_ip}"  # 用户输入的代理服务器 IP

# Prefill nodes configuration
PREFILLER_HOSTS="{prefill_p1_n1_ip} {prefill_p1_n1_ip} ... {prefill_p2_n1_ip} {prefill_p2_n1_ip} ..."
PREFILLER_PORTS="7100 7101 ... 7100 7101 ..."

# Decode nodes configuration
DECODER_HOSTS="{decode_d1_n1_ip} {decode_d1_n1_ip} ... {decode_d2_n1_ip} {decode_d2_n1_ip} ..."
DECODER_PORTS="7100 7101 ... 7100 7101 ..."

if [ "$PROXY_TYPE" == "basic" ]; then
    python load_balance_proxy_server_example.py ...
else
    python load_balance_proxy_layerwise_server_example.py ...
fi
```

**hosts/ports 计算规则**：
- `PREFILLER_HOSTS`：使用用户输入的各 Prefill 节点实际 IP，每个 IP 重复 dp_size_local 次
- `PREFILLER_PORTS`：每节点 7100 到 7100+dp_size_local-1
- `DECODER_HOSTS`：使用用户输入的各 Decode 节点实际 IP，每个 IP 重复 dp_size_local 次
- `DECODER_PORTS`：每节点 7100 到 7100+dp_size_local-1

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 生成的目录结构
- Prefill/Decode 节点数量
- 关键参数值：`dp_size_local`, `prefill_dp_size`, `decode_dp_size`, `kv_port`, `engine_id`
- proxy hosts/ports 配置