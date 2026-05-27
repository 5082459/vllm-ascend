# 步骤 4：提取模板脚本

## 目标

从模型教程中提取多节点部署的模板脚本。

## 硬性规则

- 仅从模型教程中提取代码块，不做修改。
- 所有提取的脚本保存到 `{output_dir}/sources/` 目录。
- 使用 Read 工具读取文件，使用字符串匹配定位代码块。
- 根据节点数量提取对应数量的脚本。
- 在 README 的「工作流执行日志」部分记录步骤 4 摘要。

## 提取规则

### 容器脚本

从 `sources/{model_name}.md` 的 `Environment Preparation` -> `Installation` 章节提取：

| 项目 | 提取要求 | 保存为 |
|---|---|---|
| 容器脚本 | `{code-block} bash` 格式的 Docker 命令 | `sources/start_container.sh` |

### 启动脚本

从 `sources/{model_name}.md` 的 `Multi-node Deployment` 章节提取：

| 项目 | 提取要求 | 保存为 |
|---|---|---|
| Node 0 脚本 | ````shell` 代码块 | `sources/run_node0.sh` |
| Node 1 脚本 | ````shell` 代码块 | `sources/run_node1.sh` |
| Node 2 脚本（如有） | ````shell` 代码块 | `sources/run_node2.sh` |
| Node 3 脚本（如有） | ````shell` 代码块 | `sources/run_node3.sh` |

**定位方法**：

1. 定位 `### Multi-node Deployment` 章节。
2. 根据机型定位对应 Tab-item（如有）。
3. 搜索各节点的启动脚本代码块，按顺序提取。

**注意**：根据节点数量提取对应数量的脚本。

## MyST Markdown Tab-set 结构

如果文档有 Tab-set：

```markdown
:::::{tab-set}
::::{tab-item} A2 series
... A2 相关内容 ...
::::
::::{tab-item} A3 series
... A3 相关内容 ...
::::
:::::
```

根据机型选择对应 Tab-item。

## 代码块边界识别

`````markdown
```shell
# 代码内容
...
```
`````

提取从 ` ```shell` 后一行到 ` ``` ` 前一行的内容。

## 完成后 sources 目录结构

```text
{output_dir}/sources/
├── {model_name}.md        # 模型教程文档
├── start_container.sh     # 容器启动脚本（完整）
├── run_node0.sh           # Node 0 启动脚本（完整）
├── run_node1.sh           # Node 1 启动脚本（完整）
├── run_node2.sh           # Node 2 启动脚本（完整，如有）
└── run_node3.sh           # Node 3 启动脚本（完整，如有）
```

## 错误处理

### 无法定位章节

**执行终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-06-generate.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 无法定位章节

章节：Multi-node Deployment
原因：文档中未找到对应章节标题

可能原因：
1. 该模型不支持多节点部署
2. 文档结构变化

建议：检查步骤 3 的支持检查结果。

工作流已终止。
```

### 无法找到代码块

**执行终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-06-generate.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 无法提取代码块

章节：Multi-node Deployment
位置：Node {N}
原因：未找到对应格式的代码块

建议：
1. 检查文档格式是否变化
2. 手动下载并编辑源文件

工作流已终止。
```

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 提取的脚本列表（完整路径）
- 每个脚本的来源位置（章节）