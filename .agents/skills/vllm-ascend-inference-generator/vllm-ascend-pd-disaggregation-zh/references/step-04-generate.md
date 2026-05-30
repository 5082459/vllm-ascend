# 步骤 4：生成部署树

## 目标

把 `sources/` 中的源文件落到最终部署目录结构里，完成所有占位符替换、参数计算、proxy 启动脚本生成。

## 前置条件

`sources/` 必须包含以下文件，否则按[失败终止协议](../SKILL.md#失败终止协议)结束：

| 文件 | 来源 |
|---|---|
| `{model_name}.md` | 步骤 2 |
| `pd_disaggregation_mooncake_multi_node.md` | 步骤 2 |
| `launch_online_dp.py` | 步骤 2 |
| `load_balance_proxy_server_example.py` | 步骤 2 |
| `load_balance_proxy_layerwise_server_example.py` | 步骤 2 |
| `start_container.sh` | 步骤 3 |
| `run_dp_template_prefill_node*.sh`（≥1） | 步骤 3 |
| `run_dp_template_decode_node*.sh`（≥1） | 步骤 3 |

失败提示：

```text
❌ 步骤 4 前置条件未满足

缺少文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

## 关键规则

- 拷贝文件用 Bash `cp`；改字符串用 Edit 工具；新建文件用 Write 工具。
- 输出目录命名见 [SKILL.md「输出目录命名」](../SKILL.md#输出目录命名)。
- 参数计算交给 [`scripts/compute_pd_params.py`](../scripts/compute_pd_params.py) 一次完成，不要在生成过程中临时算 `kv_port`、`engine_id`、`dp_rank_start`、proxy hosts/ports。

## 目录结构

```text
{output_dir}/
├── sources/                        # 步骤 2/3 产出，保持不动
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
└── README.md                       # 步骤 6 写入
```

## 4.1 计算参数（先算后改）

读取步骤 3 任一 Prefill 模板，从 `kv_connector_extra_config.prefill.tp_size` 取出 `prefill_tp_size`。
同样从 Decode 模板，从 `kv_connector_extra_config.decode.tp_size` 取出 `decode_tp_size`。

> **tp_size 来源约定**：模板里的 `tp_size` 是教程作者在某个特定配置下写死的值。用户配置的 `prefill_instances × nodes_per_prefill_instance` 与教程示例不同时，**继续沿用模板里的 tp_size**——它代表的是该机型 + 模型的推荐切分策略，与实例数无关；只有 `dp_size` 会随实例规模变化。如果用户在 prompt 中显式指定了 `tp_size`，以用户值为准。

调用计算脚本（路径相对于本 skill 根目录）：

```bash
python scripts/compute_pd_params.py \
  --machine-type {machine_type_short}  # "A3" or "A2"
  --prefill-instances {prefill_instances} \
  --nodes-per-prefill {nodes_per_prefill_instance} \
  --decode-instances {decode_instances} \
  --nodes-per-decode {nodes_per_decode_instance} \
  --prefill-tp-size {prefill_tp_size} \
  --decode-tp-size {decode_tp_size} \
  --prefill-ips {prefill_p1_n1_ip} {prefill_p1_n2_ip} ... \
  --decode-ips {decode_d1_n1_ip} {decode_d1_n2_ip} ... \
  --proxy-ip {proxy_ip} \
  --output {output_dir}/.pd_plan.json
```

得到的 `.pd_plan.json` 里包含每个节点的 `kv_port`、`engine_id`、`dp_rank_start`、`dp_size`、`dp_size_local`，以及 proxy 的完整 hosts/ports 列表。后续替换全部用这份 plan，不要再手算。

> 把 plan 落到磁盘是为了让步骤 5（验证）可以做"plan 与生成脚本一致"的对比。

## 4.2 生成 prefill/start_container.sh 与 decode/start_container.sh

```bash
cp sources/start_container.sh prefill/start_container.sh
cp sources/start_container.sh decode/start_container.sh
```

用 Edit 工具替换：

| 原始 | 替换为 | 说明 |
|---|---|---|
| `|vllm_ascend_version|`（如出现） | `{version}` | 教程模板有时用占位符代替具体版本号 |
| `-v <宿主机路径>:/root/.cache` | `-v {model_path}:{model_path}` | 容器内外路径一致，便于 vllm serve 直接复用 |
| 无额外挂载行 | 在模型挂载行后追加 `-v {extra_mounts}:{extra_mounts}` | 用户选择"无额外挂载"时跳过此项 |

示例：

```bash
# 原始（教程提取）
-v /mnt/sfs_turbo/.cache:/root/.cache

# 替换后（model_path=/root/.cache/DeepSeek-V4-Pro, extra_mounts=/mnt）
-v /root/.cache/DeepSeek-V4-Pro:/root/.cache/DeepSeek-V4-Pro \
-v /mnt:/mnt
```

prefill 与 decode 两份脚本内容完全相同。

## 4.3 生成各实例节点目录

按 `prefill_instances × nodes_per_prefill_instance` 与 `decode_instances × nodes_per_decode_instance` 遍历。Prefill 与 Decode 流程相同，只是参数不同：

| 角色 | 模板前缀 | kv_role | dp_size 来源 |
|---|---|---|---|
| Prefill | `run_dp_template_prefill_node` | `kv_producer` | plan.prefill_dp_size |
| Decode | `run_dp_template_decode_node` | `kv_consumer` | plan.decode_dp_size |

对每个实例 `N` 的每个节点 `M`：

### a. 拷贝 launch_online_dp.py

```bash
cp sources/launch_online_dp.py {role}/instance{N}/node{M}/launch_online_dp.py
```

文件原样使用，不做修改。

### b. 拷贝并改写 run_dp_template.sh

模板选择：
- 如果节点编号 `M` ≤ 教程模板数量，使用 `run_dp_template_{role}_node{M}.sh`
- 否则回退到 `run_dp_template_{role}_node1.sh`

```bash
cp sources/run_dp_template_{role}_node{template_idx}.sh \
   {role}/instance{N}/node{M}/run_dp_template.sh
```

用 Edit 工具替换：

| 占位符 / 原始内容 | 替换为 | 来源 |
|---|---|---|
| `/root/.cache/{model_name}` 或 `/path_to_weight/{model_name}` | `{model_path}` | step-01 |
| `{nic_name}` | 用户输入 | step-01 |
| `{local_ip}` | 当前节点 IP | step-01 |
| `kv_port` | 来自 plan | 4.1 计算 |
| `engine_id` | 来自 plan | 4.1 计算 |
| `kv_connector_extra_config.prefill.dp_size` 与 `.decode.dp_size` | 来自 plan | 4.1 计算（见下） |

**`kv_connector_extra_config.{prefill,decode}.dp_size` 替换规则**：

这段 JSON 在 prefill 模板和 decode 模板里都是**完整出现**的（双方都需要知道对端的 dp_size 才能正确建立 KV 通信）。所以无论当前在生成哪一侧的脚本，**两个 dp_size 字段都要替换**：

- `prefill.dp_size` ← `plan.prefill_dp_size`
- `decode.dp_size` ← `plan.decode_dp_size`

`tp_size` 沿用模板原值，不动。

**`kv_role` / `kv_connector` 字段**：模板里已经写好了正确值（producer 在 prefill 模板，consumer 在 decode 模板；connector 名称由教程作者决定），保留原值不替换。

### c. 写 start_serve.sh

```bash
#!/bin/bash
python launch_online_dp.py \
    --dp-size {plan.dp_size} \
    --tp-size {tp_size_from_template} \
    --dp-size-local {plan.dp_size_local} \
    --dp-rank-start {plan.dp_rank_start} \
    --dp-address {plan.instance_first_node_ip} \
    --dp-rpc-port 12321 \
    --vllm-start-port 7100
```

所有 `plan.*` 字段直接来自 4.1 的 `.pd_plan.json`。

## 4.4 生成 proxy 目录

```bash
cp sources/load_balance_proxy_server_example.py proxy/load_balance_proxy_server_example.py
cp sources/load_balance_proxy_layerwise_server_example.py proxy/load_balance_proxy_layerwise_server_example.py
```

> 这两个文件**必须**拷贝到 proxy 目录，否则 `start_proxy.sh` 找不到入口。

写 `proxy/start_proxy.sh`，hosts/ports 来自 plan.proxy 字段：

```bash
#!/bin/bash
# Proxy startup script

PROXY_TYPE="{proxy_type_short}"  # "basic" or "layerwise"
PROXY_PORT="1999"
PROXY_HOST="{plan.proxy.proxy_ip}"

PREFILLER_HOSTS="{plan.proxy.prefiller_hosts 空格连接}"
PREFILLER_PORTS="{plan.proxy.prefiller_ports 空格连接}"
DECODER_HOSTS="{plan.proxy.decoder_hosts 空格连接}"
DECODER_PORTS="{plan.proxy.decoder_ports 空格连接}"

if [ "$PROXY_TYPE" == "basic" ]; then
    python load_balance_proxy_server_example.py \
        --port $PROXY_PORT --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
else
    python load_balance_proxy_layerwise_server_example.py \
        --port $PROXY_PORT --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
fi
```

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- `.pd_plan.json` 关键字段（prefill_dp_size、decode_dp_size、prefill_dp_size_local、decode_dp_size_local）
- 各节点的 kv_port、engine_id、dp_rank_start
- proxy hosts/ports 总长度
