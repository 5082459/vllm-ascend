# 步骤 3：提取模板脚本

## 目标

从模型教程的 Single-node Deployment 章节提取容器启动脚本和 vllm serve 启动脚本。

## 关键规则

- 只提取代码块原文，不做任何修改（修改在步骤 4 进行）。
- 全部输出到 `{output_dir}/sources/`。
- 根据机型选择对应 Tab-item 的代码块。
- 提取失败时按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 文档格式判断

定位到 `### Single-node Deployment` 章节后：

- 章节内出现 `:::::{tab-set}` → 新格式（按机型分 Tab-item）
- 否则 → 旧格式（直接是平铺代码块）

## 代码块格式

教程里出现过的代码块标记：

| 标记形式 | 典型用途 |
|---|---|
| ` ```{code-block} bash` | Installation 章节 Docker 命令 |
| ` ```{code-block} shell` | 部署章节脚本 |
| ` ```shell` | 部署章节脚本 |

提取边界：
- MyST `{code-block}` 形式：起始行后的下一行开始，到下一行 ``` 结束；跳过 `:substitutions:` 等元数据行。
- 普通 ` ```shell ` 形式：起始行的下一行开始，到下一行 ``` 结束。

## Tab-set 选择

```markdown
:::::{tab-set}
::::{tab-item} A2 series
:sync: A2
... A2 配置 ...
::::
::::{tab-item} A3 series
:sync: A3
... A3 配置 ...
::::
:::::
```

按 `:sync:` 属性识别机型，不要依赖 Tab-item 出现顺序——不同教程顺序不一致。

## 提取项

### 容器脚本

来自 `Environment Preparation` → `Installation` 章节的 Docker 命令：

| 项 | 保存为 |
|---|---|
| 容器启动命令代码块 | `sources/start_container.sh` |

### 单节点启动脚本

来自 `Single-node Deployment` 章节（必要时进对应机型 Tab-item）：

| 项 | 保存为 |
|---|---|
| `vllm serve` shell 块 | `sources/run_single_node.sh` |

## 完成后 sources 目录

```text
{output_dir}/sources/
├── {model_name}.md             # 步骤 2 下载
├── start_container.sh          # 本步提取
└── run_single_node.sh          # 本步提取
```

## 失败处理

### 找到章节但提取不到代码块

```text
❌ 无法提取代码块

章节：Single-node Deployment
原因：未找到对应格式的代码块

建议：
1. 检查文档格式是否变化
2. 手动下载并编辑源文件

工作流已终止。
```

按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 文档格式判断结果（新/旧）
- 机型与命中的 Tab-item
- 提取出的脚本清单（含来源章节、Tab-item、代码块格式）
