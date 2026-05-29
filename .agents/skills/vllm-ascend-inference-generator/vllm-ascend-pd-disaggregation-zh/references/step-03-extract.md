# 步骤 3：提取模板脚本

## 目标

从模型教程的 PD 分离章节中提取部署模板：容器启动脚本、Prefill / Decode 节点模板。

## 关键规则

- 只提取代码块原文，不做任何修改（修改在步骤 4 进行）。
- 全部输出到 `{output_dir}/sources/`。
- 根据机型（A2 / A3）选择对应 Tab-item 的代码块。
- 提取失败时按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 文档格式判断

定位到 `### Prefill-Decode Disaggregation` 章节后：

- 章节内出现 `:::::{tab-set}` → 新格式（按机型分 Tab-item）
- 否则 → 旧格式（直接是平铺代码块）

## 代码块格式

教程里出现过的代码块标记：

| 标记形式 | 典型用途 |
|---|---|
| ` ```{code-block} bash` | Installation 章节的 Docker 命令 |
| ` ```{code-block} shell` | 部署章节脚本 |
| ` ```shell` | 部署章节脚本 |
| 数字列表后紧跟 ` ```shell` | PD 各节点脚本（如 "2. Prefill Node 0 ..."） |
| ` ```python` | 辅助脚本（launch_online_dp.py 等） |

提取边界：
- MyST `{code-block}` 形式：起始行后的下一行开始，到下一行 ``` 结束；跳过 `:substitutions:` 等元数据行。
- 普通 ` ```shell ` 形式：起始行的下一行开始，到下一行 ``` 结束。
- 列表项内代码块：以列表项标题作为定位锚点，再按上面任一形式提取。

某些文档使用五重反引号包裹三重反引号——这是 MyST 嵌套用法，提取时取最内层实际代码内容即可。

## Tab-set 选择

```markdown
:::::{tab-set}
:sync-group: install

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

按 `:sync:` 属性识别机型，不要依赖 Tab-item 出现顺序——不同教程顺序不一致。Tab-item 内可能仍混用 `{code-block} bash` 与 `shell` 两种格式。

## 提取项

### 容器脚本

来自 `Environment Preparation` → `Installation` 章节的 Docker 命令：

| 项 | 保存为 |
|---|---|
| 容器启动命令代码块 | `sources/start_container.sh` |

### Prefill 节点模板

进入对应机型 Tab-item，按出现顺序提取所有包含 `kv_role: kv_producer`（或 `"kv_role": "kv_producer"`）的 shell 块：

| 项 | 保存为 |
|---|---|
| 第 1 个 producer 块 | `sources/run_dp_template_prefill_node1.sh` |
| 第 2 个 producer 块 | `sources/run_dp_template_prefill_node2.sh` |
| ... | `sources/run_dp_template_prefill_node{N}.sh` |

定位方法：搜索 `kv_role` 匹配 → 向上找最近的 ` ```shell ` 起点 → 提取到下一个 ``` 终点。

### Decode 节点模板

按出现顺序提取所有 `kv_role: kv_consumer` 的 shell 块，命名规则同 Prefill：

`sources/run_dp_template_decode_node{N}.sh`

> 完整提取教程里的所有模板脚本，不做"用户配置 vs 教程数量"的匹配。用户配置可能与教程示例不一致，匹配在步骤 4 处理。

## kv-transfer-config JSON 块的特殊性

`--kv-transfer-config` 通常跟着多行 JSON：

```shell
--kv-transfer-config \
'{"kv_connector": "MooncakeConnectorV1",
"kv_role": "kv_producer",
"kv_port": "30000",
"engine_id": "0",
"kv_connector_extra_config": {
        "prefill": {"dp_size": 2, "tp_size": 8},
        "decode": {"dp_size": 32, "tp_size": 1}
    }
}'
```

提取时**完整保留整段**，直到遇到下一个独立参数或命令结束。中途不要做任何换行重排或字段顺序调整。

## 其他 `--xxx-config` JSON 块（如 `--additional-config`）

部分模型（如 DeepSeek-V4-Pro）在脚本末尾会带额外的编译/调度 JSON，例如：

```shell
--additional-config '{"ascend_compilation_config":{...}}'
```

这些块**整段原样保留**，不要解析、不要重排字段、不要在步骤 4 里替换里面的内容——它们是教程作者针对该模型调好的参数，与本 skill 的并行配置无关。

## 完成后 sources 目录

```text
{output_dir}/sources/
├── {model_name}.md                                    # 步骤 2 下载
├── pd_disaggregation_mooncake_multi_node.md           # 步骤 2 下载
├── launch_online_dp.py                                # 步骤 2 下载
├── load_balance_proxy_server_example.py               # 步骤 2 下载
├── load_balance_proxy_layerwise_server_example.py     # 步骤 2 下载
├── start_container.sh                                 # 本步提取
├── run_dp_template_prefill_node*.sh                   # 本步提取
└── run_dp_template_decode_node*.sh                    # 本步提取
```

## 失败处理

### 找不到 Prefill-Decode Disaggregation 章节

输出：

```text
❌ 无法定位章节

章节：Prefill-Decode Disaggregation
原因：文档中未找到对应章节标题

工作流已终止。
```

按[失败终止协议](../SKILL.md#失败终止协议)结束。

### 找到章节但提取不到代码块

```text
⚠️ 警告：未提取到完整模板

章节：Prefill-Decode Disaggregation
未找到 kv_role: kv_producer / kv_consumer 的 shell 代码块
已提取：{p_count} 个 Prefill 模板，{d_count} 个 Decode 模板
```

如果 `p_count == 0` 或 `d_count == 0`，按[失败终止协议](../SKILL.md#失败终止协议)结束（步骤 4 没有可用模板）。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 文档格式判断结果（新/旧）
- 机型与命中的 Tab-item
- 提取出的脚本清单（含来源章节、Tab-item、代码块格式）
