# 步骤 3：提取模板脚本

## 目标

从模型教程的 Multi-node Deployment 章节提取容器启动脚本和各节点的启动脚本。

## 关键规则

- 只提取代码块原文，不做任何修改（修改在步骤 4 进行）。
- 全部输出到 `{output_dir}/sources/`。
- 根据机型选择对应 Tab-item 的代码块。
- 提取失败时按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 文档格式判断

定位到 `### Multi-node Deployment` 章节后：

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

## 节点脚本定位

各节点脚本通常用粗体标题分隔，大小写不一致：

| 教程 | 节点标题示例 |
|---|---|
| DeepSeek-V3.1.md | `**Node 0**`、`**Node 1**` |
| GLM5.md | `**node 0**`、`**node 1**` |

定位方法：
1. 搜索节点标题（不区分大小写）
2. 向下找最近的代码块起始标记
3. 提取完整代码块直到结束标记

## 提取项

### 容器脚本

来自 `Environment Preparation` → `Installation` 章节的 Docker 命令：

| 项 | 保存为 |
|---|---|
| 容器启动命令代码块 | `sources/start_container.sh` |

### 各节点启动脚本

按节点编号顺序提取所有节点的脚本：

| 节点 | 保存为 |
|---|---|
| Node 0 | `sources/run_node0.sh` |
| Node 1 | `sources/run_node1.sh` |
| Node N | `sources/run_node{N}.sh` |

> 完整提取教程里的所有节点脚本，不做"用户配置 vs 教程数量"的匹配——匹配在步骤 4 处理。如果用户的 `node_count` 大于教程节点数，步骤 4 会以 `run_node1.sh` 为模板复制。

## 完成后 sources 目录

```text
{output_dir}/sources/
├── {model_name}.md                # 步骤 2 下载
├── start_container.sh             # 本步提取
├── run_node0.sh                   # 本步提取
├── run_node1.sh                   # 本步提取
└── run_node{N}.sh                 # 本步提取（如教程含更多节点）
```

## 失败处理

### 找到章节但提取不到代码块

```text
⚠️ 警告：未提取到完整模板

章节：Multi-node Deployment
未找到节点脚本代码块
已提取：{n_count} 个节点脚本
```

如果 `n_count == 0` 或 `< 2`（多节点至少需要 2 个），按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 文档格式判断结果（新/旧）
- 机型与命中的 Tab-item
- 提取出的脚本清单（含来源章节、Tab-item、代码块格式、节点编号）
