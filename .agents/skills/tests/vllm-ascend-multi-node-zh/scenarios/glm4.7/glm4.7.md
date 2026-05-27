# 测试用例：多节点部署 - GLM-4.7

## 测试场景

生成 GLM-4.7 多节点推理服务部署包（2节点）。

## 输入参数

| 参数 | 测试值 |
|---|---|
| deployment_mode | multi-node |
| model_name | GLM-4.7 |
| version | latest |
| machine_type | A3 |
| model_path | /root/.cache/GLM-4.7 |
| nic_name | eth0 |
| extra_mounts | /mnt |
| node_count | 2 |
| dp_size | 4 |
| tp_size | 2 |

## 预期输出目录

```text
multi_node_glm4_7_2nodes/
├── sources/
│   ├── GLM4.md
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
tp_size = 2
dp_size_local = 16 / 2 = 8
dp_size_total = 8 × 2 = 16
dp_rank_start_node0 = 0
dp_rank_start_node1 = 8
```

## 预期验证结果

| 检查项 | Node 0 预期 | Node 1 预期 |
|---|---|---|
| --headless | 不存在 | 存在 |
| --data-parallel-size | 16 | 16 |
| --data-parallel-size-local | 8 | 8 |
| --data-parallel-start-rank | 0 | 8 |
| --data-parallel-address | 192.168.1.10 | 192.168.1.10 |

## 测试执行步骤

1. 执行主技能，选择「多节点部署」
2. 调用 multi-node 子技能
3. 验证生成的目录结构（2个节点目录）
4. 验证 Node 0 无 --headless
5. 验证 Node 1 有 --headless

## 测试通过标准

- 节点目录数量 = 2
- Node 0 参数正确（无 headless，dp_rank_start=0）
- Node 1 参数正确（有 headless，dp_rank_start=8）
- README 包含启动顺序说明