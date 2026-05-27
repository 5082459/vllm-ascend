# 步骤 6：验证一致性

## 目标

验证生成的脚本符合多节点部署要求。

## 硬性规则

- 先验证文件结构完整性，再验证参数一致性。
- **sources 目录文件缺失必须立即报错终止**，不允许继续生成。
- 使用 Glob 工具检查目录结构。
- 使用 Read/Grep 工具验证脚本参数。
- 在 README 的「工作流执行日志」部分记录步骤 6 摘要。

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
Glob pattern: sources/run_node*.sh
Glob pattern: sources/start_container.sh
```

### 校验规则

| 文件模式 | 必须条件 | 失败处理 |
|---|---|---|
| `sources/run_node*.sh` | 至少匹配 node_count 个文件 | 立即报错终止 |
| `sources/start_container.sh` | 文件存在 | 立即报错终止 |

### 错误输出格式

**如果 sources 目录文件缺失**：

```text
❌ 步骤 6 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 4 未完成或提取失败

【必须先执行步骤 4】
请检查模型教程是否包含 Multi-node Deployment 章节。

工作流已终止。
```

## 第二部分：文件结构校验

**仅当 sources 目录校验通过后执行**。

**必需文件列表**：

| 文件路径 | 必需 | 说明 |
|---|---|---|
| `sources/{model_name}.md` | ✓ | 模型教程文档 |
| `sources/start_container.sh` | ✓ | 容器启动脚本源文件 |
| `sources/run_node0.sh` | ✓ | Node 0 启动脚本源文件 |
| `sources/run_node1.sh` | ✓ | Node 1 启动脚本源文件 |
| `sources/run_node2.sh` | 按节点数 | Node 2 启动脚本源文件（如有） |
| `sources/run_node3.sh` | 按节点数 | Node 3 启动脚本源文件（如有） |
| `node0/start_container.sh` | ✓ | Node 0 容器启动脚本 |
| `node0/run_serve.sh` | ✓ | Node 0 服务启动脚本 |
| `node1/start_container.sh` | ✓ | Node 1 容器启动脚本 |
| `node1/run_serve.sh` | ✓ | Node 1 服务启动脚本 |
| `node2/...` | 按节点数 | Node 2 目录（如有） |
| `node3/...` | 按节点数 | Node 3 目录（如有） |
| `README.md` | ✓ | 部署说明文档 |

**校验方法**：

```text
使用 Glob 工具检查：
{output_dir}/node*/start_container.sh
{output_dir}/node*/run_serve.sh

预期结果：节点目录数量 = 用户配置的 node_count
每个节点目录包含 2 个脚本文件
```

## 第三部分：参数一致性校验

**校验逻辑取决于 parallel_config_mode：**

### 当 parallel_config_mode = "使用模板配置" 时

**不验证 DP/TP/EP 参数值**，仅验证以下内容：

| 检查项 | 方法 | 预期结果 |
|---|---|---|
| Node 0 无 headless | 检查 `node0/run_serve.sh` | 无 `--headless` 参数 |
| Node N 有 headless | 检查 `nodeN/run_serve.sh` | 包含 `--headless` 参数 |
| node0_ip 一致性 | 检查所有节点 `--data-parallel-address` | 指向用户输入的 Node0 IP |
| rpc_port 一致性 | 检查所有节点 `--data-parallel-rpc-port` | 默认 13389 |
| 模型路径替换 | 检查路径参数已替换 | 路径参数完整 |

**说明**：使用模板配置时，DP/TP/EP 参数保持模板原值，无需验证是否匹配用户选择或计算公式。

### 当 parallel_config_mode = "自定义并行配置" 时

验证所有参数：

| 检查项 | 方法 | 预期结果 |
|---|---|---|
| Node 0 无 headless | 检查 `node0/run_serve.sh` | 无 `--headless` 参数 |
| Node N 有 headless | 检查 `nodeN/run_serve.sh` | 包含 `--headless` 参数 |
| dp_rank_start 递进 | 检查各节点 `--data-parallel-start-rank` | 按 dp_size_local 递增 |
| node0_ip 一致性 | 检查所有节点 `--data-parallel-address` | 指向 `<NODE0_IP>` 占位符 |
| DP size 一致性 | 检查所有节点 `--data-parallel-size` | 所有节点相等 |
| DP size local 一致性 | 检查所有节点 `--data-parallel-size-local` | 所有节点相等 |
| TP size 一致性 | 检查所有节点 `--tensor-parallel-size` | 匹配用户选择的 tp_size |
| EP 配置正确 | 检查 `--enable-expert-parallel` | 启用时存在，不启用时不存在 |
| rpc_port 一致性 | 检查所有节点 `--data-parallel-rpc-port` | 默认 13389 |

**验证公式**：

```text
dp_rank_start_node_n = n × dp_size_local
dp_size_total = dp_size_local × node_count
```

验证：
- Node 0: `dp_rank_start = 0`
- Node 1: `dp_rank_start = dp_size_local`
- Node N: `dp_rank_start = N × dp_size_local`

## 验证方法

### 文件结构验证

使用 Glob 工具列出各目录下的文件，对比必需文件列表，计算目录数量是否符合用户配置。

### 参数验证

使用 Grep 工具搜索关键参数：

```bash
grep -E "(--data-parallel-size|--tensor-parallel-size|--data-parallel-address|--data-parallel-start-rank|--headless)" "{script_path}"
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

缺失文件：
- {missing_file_path}

预期节点数：{expected_count}
实际节点数：{actual_count}

建议：检查步骤 4 和步骤 5 的执行日志。

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

建议：检查步骤 5 的参数计算逻辑。

工作流已终止。
```

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 文件结构检查结果（通过/失败）
- 文件数量统计
- 节点目录数量
- parallel_config_mode 值
- 当使用模板配置时：记录"跳过 DP/TP/EP 参数值验证"
- 当自定义配置时：参数检查项列表、每个检查项的结果（通过/失败）