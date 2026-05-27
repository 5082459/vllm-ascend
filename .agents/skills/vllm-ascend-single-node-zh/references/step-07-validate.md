# 步骤 6：验证一致性

## 目标

验证生成的脚本符合单节点部署要求。

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
Glob pattern: sources/run_single_node.sh
Glob pattern: sources/start_container.sh
```

### 校验规则

| 文件模式 | 必须条件 | 失败处理 |
|---|---|---|
| `sources/run_single_node.sh` | 文件存在 | 立即报错终止 |
| `sources/start_container.sh` | 文件存在 | 立即报错终止 |

### 错误输出格式

**如果 sources 目录文件缺失**：

```text
❌ 步骤 6 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 4 未完成或提取失败

【必须先执行步骤 4】
请检查模型教程是否包含 Single-node Deployment 章节。

工作流已终止。
```

## 第二部分：文件结构校验

**仅当 sources 目录校验通过后执行**。

**必需文件列表**：

| 文件路径 | 必需 | 说明 |
|---|---|---|
| `sources/{model_name}.md` | ✓ | 模型教程文档 |
| `sources/start_container.sh` | ✓ | 容器启动脚本源文件 |
| `sources/run_single_node.sh` | ✓ | 单节点启动脚本源文件 |
| `node/start_container.sh` | ✓ | 节点容器启动脚本 |
| `node/run_serve.sh` | ✓ | 节点服务启动脚本 |
| `README.md` | ✓ | 部署说明文档 |

**校验方法**：

```text
使用 Glob 工具检查：
{output_dir}/sources/*.md
{output_dir}/sources/*.sh
{output_dir}/node/*.sh
{output_dir}/README.md

预期结果：必需文件全部存在
```

## 第三部分：参数一致性校验

**校验逻辑取决于 parallel_config_mode：**

### 当 parallel_config_mode = "使用模板配置" 时

**不验证 DP/TP/EP 参数值**，仅验证以下内容：

| 检查项 | 方法 | 预期结果 |
|---|---|---|
| vllm serve 命令完整性 | 检查 `node/run_serve.sh` | 包含完整 vllm serve 参数 |
| 模型路径替换 | 检查路径参数已替换 | 路径参数完整 |
| 占位符提示 | 检查 `<LOCAL_IP>` 存在 | 用户需手动替换的占位符 |
| DP/TP 参数存在 | 检查模板参数保留 | 保持模板原值不做验证 |

**说明**：使用模板配置时，DP/TP/EP 参数保持模板原值，无需验证是否匹配用户选择。

### 当 parallel_config_mode = "自定义并行配置" 时

验证所有参数：

| 检查项 | 方法 | 预期结果 |
|---|---|---|
| vllm serve 命令完整性 | 检查 `node/run_serve.sh` | 包含完整 vllm serve 参数 |
| DP 配置正确 | 检查 `--data-parallel-size` | 匹配用户选择的 dp_size |
| TP 配置正确 | 检查 `--tensor-parallel-size` | 匹配用户选择的 tp_size |
| EP 配置正确 | 检查 `--enable-expert-parallel` | 启用时存在，不启用时不存在 |
| 无多节点参数 | 检查无 `--data-parallel-address` | 不存在多节点参数 |
| 模型路径存在 | 检查路径参数已替换 | 路径参数完整 |
| 占位符提示 | 检查 `<LOCAL_IP>` 存在 | 用户需手动替换的占位符 |

## 验证方法

### 文件结构验证

使用 Glob 工具列出各目录下的文件，对比必需文件列表。

### 参数验证

使用 Grep 工具搜索关键参数：

```bash
grep -E "(--data-parallel-size|--tensor-parallel-size|--data-parallel-address)" "{script_path}"
```

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
- parallel_config_mode 值
- 当使用模板配置时：记录"跳过 DP/TP/EP 参数值验证"
- 当自定义配置时：参数检查项列表、每个检查项的结果（通过/失败）