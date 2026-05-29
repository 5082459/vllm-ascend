# 附录：PD分离专用参考

## KV Connector 类型说明

教程里见过的 connector 类型有四种，按使用情况分两组：

| connector | 当前出现于 | 状态 |
|---|---|---|
| `MooncakeConnectorV1` | DeepSeek-V3.1、GLM5、GLM5.1 | 在用 |
| `MooncakeHybridConnector` | DeepSeek-V4-Pro、DeepSeek-V4-Flash | 在用 |
| `MooncakeConnector` | 早期版本 | 历史保留（已不在主流模板里） |
| `MooncakeLayerwiseConnector` | 早期版本 | 历史保留（已不在主流模板里） |

> 重要：本 skill 一律**保留模板里的 connector 原值**，不做名称替换。教程会随版本演化新增/替换 connector，硬编码替换规则只会让产出与教程脱节。

### kv_transfer_config 通用配置

无论 connector 是哪一种，`kv_transfer_config` 的字段结构都一致：

```json
{
  "kv_connector": "<模板原值>",
  "kv_role": "kv_producer" | "kv_consumer",
  "kv_port": "{kv_port}",
  "engine_id": "{engine_id}",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": X, "tp_size": Y},
    "decode": {"dp_size": X, "tp_size": Y}
  }
}
```

需要替换的只有 `kv_port`、`engine_id` 与 `kv_connector_extra_config.{prefill,decode}.dp_size`——其它字段保留模板原值。

### kv_port 端口范围

| 机型 | 卡数 | 保留端口范围 | 建议 kv_port |
|---|---|---|---|
| A2 | 8 | 20000 - 27999 | ≥ 28000 |
| A3 | 16 | 20000 - 35999 | ≥ 36000 |

**注意**：kv_port 公式以 `36000` 为基数，同时满足 A2（≥28000）和 A3（≥36000）的要求。每个实例的 kv_port 必须唯一，按 100 递增分配（如 36000, 36100, 36200）。

### 代理类型与 connector 的关系

| 代理脚本 | 默认搭配的 connector 家族 | 路由方向 |
|---|---|---|
| `load_balance_proxy_server_example.py` | 以 prefill→decode 推送为主（`MooncakeConnector` 系） | P → D |
| `load_balance_proxy_layerwise_server_example.py` | 以 decode 拉取为主（`MooncakeLayerwiseConnector` 系） | D → P |

> `MooncakeConnectorV1` 和 `MooncakeHybridConnector` 在不同教程里都搭配过这两个 proxy 中的某一个；具体配对以教程模板为准，不要凭名字猜。本 skill 同时把两份 proxy 脚本拷贝到 `proxy/` 目录，由 `start_proxy.sh` 的 `PROXY_TYPE` 变量切换，部署时按教程或用户输入选用。

## 代理启动参数详解

### 参数格式

```text
--prefiller-hosts: 空格分隔的 IP 列表，每个节点重复 dp_size_local 次
--prefiller-ports: 空格分隔的端口列表，格式为 vllm_start_port + i (i=0..dp_size_local-1)
--decoder-hosts: 空格分隔的 IP 列表，每个节点重复 dp_size_local 次
--decoder-ports: 空格分隔的端口列表
```

### 完整示例

**A3 配置（2P1D，TP=1，DP=16）**：

```shell
python load_balance_proxy_layerwise_server_example.py \
  --port 1999 \
  --host 192.0.0.100 \
  --prefiller-hosts 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 192.0.0.1 \
                   192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 192.0.0.2 \
  --prefiller-ports 7100 7101 7102 7103 7104 7105 7106 7107 7108 7109 7110 7111 7112 7113 7114 7115 \
                    7100 7101 7102 7103 7104 7105 7106 7107 7108 7109 7110 7111 7112 7113 7114 7115 \
  --decoder-hosts 192.0.0.3 192.0.0.3 ...×16 \
  --decoder-ports 7100 7101 ... 7115
```

**A2 配置（4×1P 1×4D，TP=1，DP=8）**：

```shell
python load_balance_proxy_layerwise_server_example.py \
  --port 1999 \
  --host 192.0.0.100 \
  --prefiller-hosts P1_IP ...×8 P2_IP ...×8 P3_IP ...×8 P4_IP ...×8 \
  --prefiller-ports 7100 7101 ... 7107 (重复4次) \
  --decoder-hosts D1_IP ...×8 D2_IP ...×8 D3_IP ...×8 D4_IP ...×8 \
  --decoder-ports 7100 7101 ... 7107 (重复4次，共32个端口)
```

## PD分离参数计算公式

### 公共参数

```text
单机卡数 = (machine_type == "A3超节点") ? 16 : 8
```

### Prefill 参数

```text
prefill_tp_size = kv_connector_extra_config.prefill.tp_size
prefill_dp_size_local = 单机卡数 / prefill_tp_size
prefill_dp_size = prefill_instances × nodes_per_prefill_instance × prefill_dp_size_local
prefill_kv_port = 36000 + instance_index × 100
prefill_engine_id = instance_index + 1 (1, 2, 3...)
prefill_dp_rank_start = (node_index - 1) × prefill_dp_size_local (各实例独立计数)
```

### Decode 参数

```text
decode_tp_size = kv_connector_extra_config.decode.tp_size
decode_dp_size_local = 单机卡数 / decode_tp_size
decode_dp_size = decode_instances × nodes_per_decode_instance × decode_dp_size_local
decode_kv_port = 36000 + prefill_instances × 100 + instance_index × 100
decode_engine_id = prefill_count + instance_index + 1 (继续递增)
decode_dp_rank_start = (node_index - 1) × decode_dp_size_local (各实例独立计数，与 Prefill 一致)
```

**重要**：dp_rank_start 计算规则与 [step-04-generate.md](step-04-generate.md) 一致：单个实例内按节点递增，各实例独立计算。不要使用全局递增公式。生成时直接调用 [`scripts/compute_pd_params.py`](../scripts/compute_pd_params.py) 即可，无需手算。

### 示例配置（2P1D，A3，Prefill TP=8，Decode TP=4）

```text
# Prefill 和 Decode 可能使用不同 tp_size，均从 kv_connector_extra_config 获取
单机卡数 = 16
prefill_tp_size = kv_connector_extra_config.prefill.tp_size  # 例如 8
decode_tp_size = kv_connector_extra_config.decode.tp_size   # 例如 4
prefill_dp_size_local = 16 / 8 = 2
decode_dp_size_local = 16 / 4 = 4

Prefill:
prefill_dp_size = 2 × 1 × 2 = 4
P1N1: kv_port=36000, engine_id=1, dp_rank_start=0
P2N1: kv_port=36100, engine_id=2, dp_rank_start=0

Decode:
decode_dp_size = 1 × 1 × 4 = 4
D1N1: kv_port=36200, engine_id=3, dp_rank_start=0
```

**多实例 Decode dp_rank_start 示例**（4D2N，A3，decode_dp_size_local=4）：

```text
D1N1: dp_rank_start=0, D1N2: dp_rank_start=4  (实例1独立计数)
D2N1: dp_rank_start=0, D2N2: dp_rank_start=4  (实例2独立计数)
D3N1: dp_rank_start=0, D3N2: dp_rank_start=4  (实例3独立计数)
D4N1: dp_rank_start=0, D4N2: dp_rank_start=4  (实例4独立计数)
```

## 代理 hosts/ports 生成规则

### Prefill hosts

```text
格式：P1N1_IP × dp_size_local P1N2_IP × dp_size_local ... P2N1_IP × dp_size_local ...

生成：遍历所有 Prefill 节点，每个节点 IP 重复 dp_size_local 次
```

### Prefill ports

```text
格式：7100 7101 ... (到 7100+dp_size_local-1) 对每个节点重复

生成：遍历所有 Prefill 节点，每节点生成 dp_size_local 个端口
```

### Decode hosts/ports

同理，遍历所有 Decode 节点生成。