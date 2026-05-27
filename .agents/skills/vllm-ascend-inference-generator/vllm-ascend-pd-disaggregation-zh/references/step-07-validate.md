# 步骤 7：验证一致性

## 目标

验证生成的脚本符合 PD分离部署要求。

## 硬性规则

- 先验证文件结构完整性，再验证参数一致性。
- **sources 目录文件缺失必须立即报错终止**，不允许继续生成。
- 使用 Glob 工具检查目录结构。
- 使用 Read/Grep 工具验证脚本参数。
- 在 README 的「工作流执行日志」部分记录步骤 7 摘要。

**终止流程定义**：
当校验失败时，必须按顺序执行：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

## 第一部分：sources 目录强制校验

**这是最关键的校验步骤，必须在其他校验之前执行**。

### 校验操作

使用 Glob 工具逐一检查：

```
Glob pattern: sources/run_dp_template_prefill_node*.sh
Glob pattern: sources/run_dp_template_decode_node*.sh
Glob pattern: sources/start_container.sh
```

### 校验规则

| 文件模式 | 必须条件 | 失败处理 |
|---|---|---|
| `sources/run_dp_template_prefill_node*.sh` | 至少匹配 1 个文件 | 立即报错终止 |
| `sources/run_dp_template_decode_node*.sh` | 至少匹配 1 个文件 | 立即报错终止 |
| `sources/start_container.sh` | 文件存在 | 立即报错终止 |
| `sources/launch_online_dp.py` | 文件存在 | 立即报错终止 |

### 错误输出格式

**如果 sources 目录文件缺失**：

```text
❌ 步骤 7 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 5 未完成或提取失败

【必须先执行步骤 5】
请检查模型教程是否包含 Prefill-Decode Disaggregation 章节。

工作流已终止。
```

## 第二部分：文件结构校验

**仅当 sources 目录校验通过后执行**。

**sources 目录必需文件**：

| 文件路径 | 必需 |
|---|---|
| `sources/{model_name}.md` | ✓ |
| `sources/pd_disaggregation_mooncake_multi_node.html` | ✓ |
| `sources/launch_online_dp.py` | ✓ |
| `sources/run_dp_template_prefill_node*.sh` | ✓ |
| `sources/run_dp_template_decode_node*.sh` | ✓ |
| `sources/load_balance_proxy_server_example.py` | ✓ |
| `sources/load_balance_proxy_layerwise_server_example.py` | ✓ |
| `sources/start_container.sh` | ✓ |

**prefill 目录校验**：

按 `prefill_instances × nodes_per_prefill_instance` 计算：

| 目录路径 | 必需文件 |
|---|---|
| `prefill/start_container.sh` | ✓ |
| `prefill/instance{N}/node{M}/launch_online_dp.py` | ✓ |
| `prefill/instance{N}/node{M}/run_dp_template.sh` | ✓ |
| `prefill/instance{N}/node{M}/start_serve.sh` | ✓ |

**decode 目录校验**：

按 `decode_instances × nodes_per_decode_instance` 计算：

| 目录路径 | 必需文件 |
|---|---|
| `decode/start_container.sh` | ✓ |
| `decode/instance{N}/node{M}/launch_online_dp.py` | ✓ |
| `decode/instance{N}/node{M}/run_dp_template.sh` | ✓ |
| `decode/instance{N}/node{M}/start_serve.sh` | ✓ |

**proxy 目录校验**：

| 文件路径 | 必需 |
|---|---|
| `proxy/load_balance_proxy_server_example.py` | ✓ |
| `proxy/load_balance_proxy_layerwise_server_example.py` | ✓ |
| `proxy/start_proxy.sh` | ✓ |

**校验方法**：

使用 Glob 工具检查：
- Prefill instance 数量 = prefill_instances
- 每个 Prefill instance 的 node 数量 = nodes_per_prefill_instance
- Decode instance 数量 = decode_instances
- 每个 Decode instance 的 node 数量 = nodes_per_decode_instance
- proxy 目录包含 3 个文件

## 第三部分：参数一致性校验

| 检查项 | 方法 | 预期结果 |
|---|---|---|
| Prefill kv_role | 检查 Prefill 节点 | `kv_producer` |
| Decode kv_role | 检查 Decode 节点 | `kv_consumer` |
| kv_connector 存在 | 检查 kv_connector 参数 | 存在且有效（不验证具体类型） |
| Prefill dp_size 一致性 | 检查同一实例内节点 | 实例内一致 |
| Decode dp_size 一致性 | 检查同一实例内节点 | 实例内一致 |
| tp_size 存在 | 检查 --tensor-parallel-size 参数 | 存在（不验证具体值） |
| kv-transfer-config 完整性 | 检查 JSON 配置 | 包含 prefill/decode 配置 |
| launch_online_dp.py 存在 | 检查每个节点目录 | 文件存在 |
| engine_id 递增 | 检查各实例 engine_id | 按顺序递增 |
| kv_port 避免 Reserved Range | 检查 kv_port 值 | A3: >= 36000; A2: >= 28000 |
| proxy hosts 数量 | 检查 proxy 启动脚本 | hosts 数量 = 总 DP 数 |

**验证公式**：

```text
prefill_dp_size = prefill_instances × nodes_per_prefill_instance × dp_size_local
prefill_kv_port = 36000 + instance_index × 100

decode_dp_size = decode_instances × nodes_per_decode_instance × dp_size_local
decode_kv_port = 与 Prefill 实例对应或继续递增
```

## 验证方法

### 文件结构验证

使用 Glob 工具列出各目录下的文件，计算目录数量是否符合用户配置。

### 参数验证

使用 Grep 工具搜索关键参数：

```bash
grep -E "(kv_role|kv_connector|kv_port|engine_id|--dp-size|--tp-size)" "{script_path}"
```

比较各节点的参数值是否符合计算规则。

## 错误处理

### 文件结构验证失败

**执行终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 文件结构验证失败

缺失文件：{missing_file_path}
预期 Prefill instance 数量：{expected_prefill}
实际 Prefill instance 数量：{actual_prefill}

工作流已终止。
```

### 参数验证失败

**执行终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 参数一致性验证失败

检查项：{check_item}
文件：{script_path}
预期结果：{expected}
实际结果：{actual}

工作流已终止。
```

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 文件结构检查结果
- Prefill/Decode 节点数量验证
- 参数检查项列表
- 每个检查项的结果