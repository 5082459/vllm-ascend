# 测试用例：PD分离部署 - GLM5.1 (6P2N 4D2N)

## 执行指令

**重要：这是一个自动化测试场景。所有参数已在下方参数表中预定义。**

执行规则：
- **跳过所有 AskUserQuestion 交互式问答**
- **直接从参数表读取所有参数值**
- **不要请求用户确认或输入**
- **按照参数表中的值直接执行 PD 分离部署流程**
- **输出目录名称使用：pd_disaggregation_glm5_1_6p2n_4d2n**

## 测试场景

生成 GLM5.1 PD分离推理服务部署包（6个Prefill实例×2节点 + 4个Decode实例×2节点）。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | pd-disaggregation |
| model_name | GLM5.1 |
| version | 0.18.0 |
| machine_type | A3 |
| model_path | /root/.cache/GLM5.1 |
| extra_mounts | /mnt |
| nic_name | eth0 |
| prefill_instances | 6 |
| decode_instances | 4 |
| nodes_per_prefill_instance | 2 |
| nodes_per_decode_instance | 2 |
| proxy_type | 基础版本 |
| prefill_p1_n1_ip | 192.168.1.101 |
| prefill_p1_n2_ip | 192.168.1.102 |
| prefill_p2_n1_ip | 192.168.1.103 |
| prefill_p2_n2_ip | 192.168.1.104 |
| prefill_p3_n1_ip | 192.168.1.105 |
| prefill_p3_n2_ip | 192.168.1.106 |
| prefill_p4_n1_ip | 192.168.1.107 |
| prefill_p4_n2_ip | 192.168.1.108 |
| prefill_p5_n1_ip | 192.168.1.109 |
| prefill_p5_n2_ip | 192.168.1.110 |
| prefill_p6_n1_ip | 192.168.1.111 |
| prefill_p6_n2_ip | 192.168.1.112 |
| decode_d1_n1_ip | 192.168.2.101 |
| decode_d1_n2_ip | 192.168.2.102 |
| decode_d2_n1_ip | 192.168.2.103 |
| decode_d2_n2_ip | 192.168.2.104 |
| decode_d3_n1_ip | 192.168.2.105 |
| decode_d3_n2_ip | 192.168.2.106 |
| decode_d4_n1_ip | 192.168.2.107 |
| decode_d4_n2_ip | 192.168.2.108 |
| proxy_ip | 192.168.3.1 |

## 预期输出目录

```text
pd_disaggregation_glm5_1_6p2n_4d2n/
├── sources/
│   ├── GLM5.md
│   ├── pd_disaggregation_mooncake_multi_node.md
│   ├── launch_online_dp.py
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   ├── run_dp_template_prefill_node*.sh
│   ├── run_dp_template_decode_node*.sh
│   └── start_container.sh
├── prefill/
│   ├── start_container.sh
│   ├── instance1/node1/, node2/
│   ├── instance2/node1/, node2/
│   ├── instance3/node1/, node2/
│   ├── instance4/node1/, node2/
│   ├── instance5/node1/, node2/
│   └── instance6/node1/, node2/
├── decode/
│   ├── start_container.sh
│   ├── instance1/node1/, node2/
│   ├── instance2/node1/, node2/
│   ├── instance3/node1/, node2/
│   └── instance4/node1/, node2/
├── proxy/
│   ├── load_balance_proxy_server_example.py
│   ├── load_balance_proxy_layerwise_server_example.py
│   └── start_proxy.sh
└── README.md
```

## 参数计算预期

```text
单机卡数 = 16 (A3)
GLM5 Prefill tp_size = 16 (从模板获取)
GLM5 Decode tp_size = 4 (从模板获取，与Prefill不同)

Prefill:
dp_size_local = 16 / 16 = 1
prefill_dp_size = 6 × 2 × 1 = 12
kv_port分配: P1=36000, P2=36100, P3=36200, P4=36300, P5=36400, P6=36500
engine_id: 1, 2, 3, 4, 5, 6

Decode:
dp_size_local = 16 / 4 = 4
decode_dp_size = 4 × 2 × 4 = 32
kv_port分配: D1=36600, D2=36700, D3=36800, D4=36900
engine_id: 7, 8, 9, 10 (接续Prefill)

Decode dp_rank_start:
D1N1: 0, D1N2: 4
D2N1: 8, D2N2: 12
D3N1: 16, D3N2: 20
D4N1: 24, D4N2: 28
```

## Proxy 配置预期

```text
PROXY_HOST=192.168.3.1
PREFILLER_HOSTS= P1N1 P1N2 P2N1 P2N2 ... P6N1 P6N2 (共12个)
PREFILLER_PORTS= 7100 (重复12次，因dp_size_local=1)
DECODER_HOSTS= D1N1×4 D1N2×4 ... D4N1×4 D4N2×4 (共32个)
DECODER_PORTS= 7100 7101 7102 7103 (重复8次，因dp_size_local=4)
```

## 测试执行步骤

1. 执行主技能，选择「PD分离部署」
2. 调用 pd-disaggregation 子技能
3. 验证生成的目录结构（prefill/decode/proxy/sources）
4. 验证 Prefill 包含 6 个实例，每实例 2 节点
5. 验证 Decode 包含 4 个实例，每实例 2 节点
6. 验证 kv_role/kv_port/engine_id 参数正确
7. 验证 README 包含工作流执行日志

## 测试通过标准

- 目录结构完整（prefill/decode/proxy/sources）
- Prefill: 6实例×2节点 = 12节点
- Decode: 4实例×2节点 = 8节点
- Prefill kv_role = kv_producer
- Decode kv_role = kv_consumer
- kv_port 配置正确（Prefill 36000-36500, Decode 36600-36900）
- engine_id 配置正确（Prefill 1-6, Decode 7-10）
- kv_connector = MooncakeConnectorV1
- README 包含「工作流执行日志」章节