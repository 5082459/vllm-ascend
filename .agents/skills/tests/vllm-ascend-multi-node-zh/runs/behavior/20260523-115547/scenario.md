# 测试用例：多节点部署

## 测试场景

生成 DeepSeek-V3.1 多节点推理服务部署包（2节点）。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | multi-node |
| model_name | DeepSeek-V3.1 |
| version | latest |
| machine_type | A3 |
| model_path | /root/.cache/DeepSeek-V3.1 |
| nic_name | eth0 |
| extra_mounts | /mnt |
| node_count | 2 |
| dp_size | 2 |
| tp_size | 8 |
| ip_mode | 默认占位符 |

## 预期输出目录

```text
multi_node_deepseek_v3_1_2nodes/
├── sources/
│   ├── DeepSeek-V3.1.md
│   ├── start_container.sh
│   ├── run_node0.sh
│   └── run_node1.sh
├── node0/
│   ├── start_container.sh
│   └── run_serve.sh
├── node1/
│   ├── start_container.sh
│   └── run_serve.sh
└── README.md
```

## 参数计算预期

```text
单机卡数 = 16
tp_size = 8
dp_size_local = 16 / 8 = 2
dp_size_total = 2 × 2 = 4
dp_rank_start_node0 = 0
dp_rank_start_node1 = 2
```

## 预期验证结果

| 检查项 | Node 0 预期 | Node 1 预期 |
|---|---|---|
| --headless | 不存在 | 存在 |
| --data-parallel-size | 4 | 4 |
| --data-parallel-size-local | 2 | 2 |
| --data-parallel-start-rank | 0 | 2 |
| --data-parallel-address | <NODE0_IP> | <NODE0_IP> |
| --data-parallel-rpc-port | 13389 | 13389 |

## 测试执行步骤

1. 执行主技能，选择「多节点部署」
2. 调用 multi-node 子技能
3. 验证生成的目录结构（2个节点目录）
4. 验证 Node 0 无 --headless
5. 验证 Node 1 有 --headless
6. 验证 dp_rank_start 递进正确

## 测试通过标准

- 节点目录数量 = 2
- Node 0 参数正确（无 headless，dp_rank_start=0）
- Node 1 参数正确（有 headless，dp_rank_start=2）
- README 包含启动顺序说明