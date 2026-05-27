# 附录：PD分离专用参考

## KV Connector 类型说明

### kv_transfer_config 配置

**MooncakeConnector（基础版本）**：

```json
{
  "kv_connector": "MooncakeConnector",
  "kv_role": "kv_producer" | "kv_consumer",
  "kv_port": "{kv_port}",
  "engine_id": "{engine_id}",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": X, "tp_size": Y},
    "decode": {"dp_size": X, "tp_size": Y}
  }
}
```

**MooncakeLayerwiseConnector（分层版本）**：

```json
{
  "kv_connector": "MooncakeLayerwiseConnector",
  "kv_role": "kv_producer" | "kv_consumer",
  "kv_port": "{kv_port}",
  "engine_id": "{engine_id}",
  "kv_connector_extra_config": {
    "prefill": {"dp_size": X, "tp_size": Y},
    "decode": {"dp_size": X, "tp_size": Y}
  }
}
```

### kv_port 端口范围

| 机型 | 卡数 | kv_port 范围 |
|---|---|---|
| A2 | 8 | ≥ 28000 |
| A3 | 16 | ≥ 36000 |

**注意**：每个实例的 kv_port 必须唯一，通常按 engine_id 递增分配（如 36000, 36100, 36200）。

### 代理类型与 kv_connector 对应关系

| 代理脚本 | 配合的 kv_connector | 路由方向 | 说明 |
|---|---|---|---|
| `load_balance_proxy_server_example.py` | MooncakeConnector | P → D | Prefill 发送 KV Cache 到 Decode |
| `load_balance_proxy_layerwise_server_example.py` | MooncakeLayerwiseConnector | D → P | Decode 按需从 Prefill 拉取 KV Cache |

**注意**：如果模板使用其他 kv_connector 类型（如 NpuConnector），保持原值不变，不进行替换。

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

### Prefill 参数

```text
prefill_dp_size = prefill_instances × nodes_per_prefill_instance × dp_size_local
prefill_kv_port = 36000 + instance_index × 100
prefill_engine_id = instance_index + 1 (1, 2, 3...)
prefill_dp_rank_start = 0 (各实例独立计数)
```

### Decode 参数

```text
decode_dp_size = decode_instances × nodes_per_decode_instance × dp_size_local
decode_kv_port = 与 Prefill 实例相同或继续递增
decode_engine_id = prefill_count + instance_index + 1 (继续递增)
decode_dp_rank_start = instance_index × nodes_per_instance × dp_size_local (全局递增)
```

### 示例配置（2P1D，A3，TP=8）

```text
# 注意：tp_size 从模板中获取，保持原值不变
单机卡数 = 16
tp_size = 8  # 从模板中获取
dp_size_local = 16 / 8 = 2

Prefill:
prefill_dp_size = 2 × 1 × 2 = 4
P1N1: kv_port=36000, engine_id=1, dp_rank_start=0
P2N1: kv_port=36100, engine_id=2, dp_rank_start=0

Decode:
decode_dp_size = 1 × 1 × 2 = 2
D1N1: kv_port=36200, engine_id=3, dp_rank_start=0
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