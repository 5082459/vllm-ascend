# 测试用例：PD分离部署 - GLM5 (1P1N 1D1N)

## 执行指令

**重要：这是一个自动化测试场景。所有参数已在下方参数表中预定义。**

执行规则：
- **跳过所有 AskUserQuestion 交互式问答**
- **直接从参数表读取所有参数值**
- **不要请求用户确认或输入**
- **按照参数表中的值直接执行 PD 分离部署流程**
- **输出目录名称使用：pd_disaggregation_glm5_1p1n_1d1n**

## 测试场景

生成 GLM5 PD分离推理服务部署包（1个Prefill实例×1节点 + 1个Decode实例×1节点）。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | pd-disaggregation |
| model_name | GLM5 |
| version | 0.18.0 |
| machine_type | A3 |
| model_path | /root/.cache/GLM5 |
| extra_mounts | /mnt |
| nic_name | eth0 |
| prefill_instances | 1 |
| decode_instances | 1 |
| nodes_per_prefill_instance | 1 |
| nodes_per_decode_instance | 1 |
| proxy_type | 基础版本 |
| prefill_p1_n1_ip | 192.168.1.20 |
| decode_d1_n1_ip | 192.168.1.30 |
| proxy_ip | 192.168.1.40 |

## 预期输出目录

```text
pd_disaggregation_glm5_1p1n_1d1n/
├── sources/
│   ├── GLM5.md
│   ├── launch_online_dp.py
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   ├── run_dp_template_prefill_node*.sh
│   ├── run_dp_template_decode_node*.sh
│   └── start_container.sh
├── prefill/
│   ├── start_container.sh
│   └── instance1/
│       └── node1/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
├── decode/
│   ├── start_container.sh
│   └── instance1/
│       └── node1/
│           ├── launch_online_dp.py
│           ├── run_dp_template.sh
│           └── start_serve.sh
├── proxy/
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_proxy.sh
└── README.md
```

## 参数计算预期

```text
单机卡数 = 8 (从模板配置推导)
tp_size = 8 (从模板获取)
dp_size_local = 8 / 8 = 1

prefill_dp_size = 1 × 1 × 1 = 1
decode_dp_size = 1 × 1 × 1 = 1

Prefill:
P1N1: kv_port=36000, engine_id=1, dp_rank_start=0

Decode:
D1N1: kv_port=36200, engine_id=2, dp_rank_start=0
```

## 预期验证结果

| 检查项 | Prefill Node 1 预期 | Decode Node 1 预期 |
|---|---|---|
| kv_role | kv_producer | kv_consumer |
| kv_port | 36000 | 36200 |
| engine_id | 1 | 2 |
| kv_connector | MooncakeConnectorV1 | MooncakeConnectorV1 |
| local_ip | 192.168.1.20 | 192.168.1.30 |
| --tensor-parallel-size | 8 | 8 |
| prefill.dp_size | 1 | 1 |
| decode.dp_size | 1 | 1 |
| use_ascend_direct | true | true |

## Proxy 配置预期

```text
PROXY_HOST=192.168.1.40
PREFILLER_HOSTS=192.168.1.20
PREFILLER_PORTS=7100
DECODER_HOSTS=192.168.1.30
DECODER_PORTS=7100
```

## 测试执行步骤

1. 执行主技能，选择「PD分离部署」
2. 调用 pd-disaggregation 子技能
3. 验证生成的目录结构（prefill/decode/proxy/sources）
4. 验证 Prefill 实例包含 instance1/node1
5. 验证 Decode 实例包含 instance1/node1
6. 验证 kv_role/kv_port/engine_id 参数正确
7. 验证 README 包含工作流执行日志

## 测试通过标准

- 目录结构完整（prefill/decode/proxy/sources）
- Prefill: 1实例×1节点
- Decode: 1实例×1节点
- Prefill kv_role = kv_producer
- Decode kv_role = kv_consumer
- kv_port 配置正确（Prefill 36000, Decode 36200）
- engine_id 配置正确（Prefill 1, Decode 2）
- kv_connector = MooncakeConnectorV1
- README 包含「工作流执行日志」章节