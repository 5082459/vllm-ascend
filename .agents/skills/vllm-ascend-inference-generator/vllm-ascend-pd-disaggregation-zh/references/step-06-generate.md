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

- **文件操作方式**：
  - 从 sources 目录拷贝文件：使用 Bash `cp` 命令
  - 替换占位符：使用 Edit 工具进行字符串替换
  - 新生成文件：使用 Write 工具
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
│   ├── pd_disaggregation_mooncake_multi_node.md
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

见 [appendix-pd-resources.md](appendix-pd-resources.md)「PD分离参数计算公式」章节。

## kv_port 配置要求

见 [appendix-pd-resources.md](appendix-pd-resources.md)「kv_port 端口范围」章节。

## 生成步骤

### 步骤 1：拷贝容器脚本

**操作方式**：先 `cp` 拷贝，再 `Edit` 替换占位符。

1. **拷贝容器脚本**：
   ```bash
   cp sources/start_container.sh prefill/start_container.sh
   cp sources/start_container.sh decode/start_container.sh
   ```

2. **替换挂载路径**（使用 Edit 工具）：

   教程原始格式：`-v /mnt/sfs_turbo/.cache:/root/.cache`

   **替换规则**：

   | 原始内容 | 替换为 | 说明 |
   |---|---|---|
   | `-v <宿主机路径>:/root/.cache` | `-v {model_path}:{model_path}` | 宿主机与容器内路径保持一致 |
   | 无额外挂载 | `-v {extra_mounts}:{extra_mounts}` | 在模型挂载行后添加 |

   **说明**：使用 `{model_path}:{model_path}` 挂载方式，确保容器内路径与宿主机路径一致，run_dp_template.sh 直接使用 `{model_path}` 作为 vllm serve 模型路径。

   **示例**：
   ```bash
   # 原始（从教程提取）
   -v /mnt/sfs_turbo/.cache:/root/.cache

   # 替换后
   -v /root/.cache/DeepSeek-V4-Pro:/root/.cache/DeepSeek-V4-Pro \
   -v /mnt:/mnt
   ```

3. **最终生成文件**：prefill/start_container.sh、decode/start_container.sh

**注意**：prefill 和 decode 的 start_container.sh 内容相同，修改点一致。

### 步骤 2：生成 PD 实例节点目录

遍历 Prefill 和 Decode 实例，为每个节点生成目录和脚本。Prefill 和 Decode 的生成逻辑相同，仅参数不同。

**遍历规则**：

| 角色 | 遍历范围 | 模板前缀 | kv_role | dp_size |
|------|----------|----------|---------|---------|
| Prefill | `prefill_instances × nodes_per_prefill_instance` | `run_dp_template_prefill_node` | `kv_producer` | prefill_dp_size |
| Decode | `decode_instances × nodes_per_decode_instance` | `run_dp_template_decode_node` | `kv_consumer` | decode_dp_size |

对每个实例 N 的每个节点 M，按以下顺序操作：

1. **拷贝 launch_online_dp.py**（无需修改）：

   使用 Bash `cp` 命令直接拷贝：
   ```bash
   cp sources/launch_online_dp.py {role}/instance{N}/node{M}/launch_online_dp.py
   ```

   **注意**：此文件无需任何修改，直接拷贝即可。

2. **拷贝 run_dp_template.sh**：

   **模板选择规则**：
   - Prefill 节点：使用 `sources/run_dp_template_prefill_node{编号}.sh`
   - Decode 节点：使用 `sources/run_dp_template_decode_node{编号}.sh`
   - 如果节点编号 `{M}` <= 教程模板数量：使用对应编号的模板
   - 如果节点编号 `{M}` > 教程模板数量：使用 `node1.sh` 作为基础模板

   **操作方式**：先 `cp` 拷贝，再 `Edit` 替换占位符。

   a. **拷贝模板文件**（按节点类型区分）：

   **Prefill 节点**：
   ```bash
   cp sources/run_dp_template_prefill_node{模板编号}.sh prefill/instance{N}/node{M}/run_dp_template.sh
   ```

   **Decode 节点**：
   ```bash
   cp sources/run_dp_template_decode_node{模板编号}.sh decode/instance{N}/node{M}/run_dp_template.sh
   ```

   b. **替换占位符**（使用 Edit 工具，按表格顺序依次替换）：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/root/.cache/{model_name}` 或 `/path_to_weight/{model_name}` | 用户提供的模型路径 `{model_path}` | vllm serve 模型路径，与容器挂载路径一致 |
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

3. **生成 start_serve.sh**（使用 Write 工具）：

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

1. **拷贝代理脚本**（使用 Bash `cp` 命令，无需修改）：
   ```bash
   cp sources/load_balance_proxy_server_example.py proxy/load_balance_proxy_server_example.py
   cp sources/load_balance_proxy_layerwise_server_example.py proxy/load_balance_proxy_layerwise_server_example.py
   ```

   **注意**：代理脚本无需修改，直接拷贝即可。

2. **生成 start_proxy.sh**（使用 Write 工具）：

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
    python load_balance_proxy_server_example.py \
        --port $PROXY_PORT \
        --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
else
    python load_balance_proxy_layerwise_server_example.py \
        --port $PROXY_PORT \
        --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
fi
```

**hosts/ports 计算规则**：

见 [appendix-pd-resources.md](appendix-pd-resources.md)「代理 hosts/ports 生成规则」章节。

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 生成的目录结构
- Prefill/Decode 节点数量
- 关键参数值：`dp_size_local`, `prefill_dp_size`, `decode_dp_size`, `kv_port`, `engine_id`
- proxy hosts/ports 配置