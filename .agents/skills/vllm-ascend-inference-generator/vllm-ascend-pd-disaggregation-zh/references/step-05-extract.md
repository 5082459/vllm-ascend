# 步骤 5：提取模板脚本

## 目标

从模型教程中提取PD分离部署的模板脚本。

## 硬性规则

- 仅从模型教程中提取代码块，不做修改。
- 所有提取的脚本保存到 `{output_dir}/sources/` 目录。
- 根据机型选择对应的 PD 配置模板（A2/A3 可能有不同的配置）。
- 在 README 的「工作流执行日志」部分记录步骤 5 摘要。

## 文档格式判断

搜索 `### Prefill-Decode Disaggregation` 章节内的内容：

- 如果存在 `:::::{tab-set}` → 新格式（有 A2/A3 区分）
- 否则 → 旧格式

**注意**：launch_online_dp.py 已在步骤 4 下载，不从教程提取。

## 提取规则

### 容器脚本

从 `sources/{model_name}.md` 的 `Environment Preparation` -> `Installation` 章节提取：

| 项目 | 提取要求 | 保存为 |
|---|---|---|
| 容器脚本 | `{code-block} bash` 格式的 Docker 命令 | `sources/start_container.sh` |

### Prefill 节点模板脚本

进入对应机型的 Tab-item 区域，提取所有 `kv_role: kv_producer` 的 shell 块：

| 项目 | 提取位置 | 保存为 |
|---|---|---|
| Prefill node 1 | 第一个 `kv_role: kv_producer` shell 块 | `sources/run_dp_template_prefill_node1.sh` |
| Prefill node 2 | 第二个 `kv_role: kv_producer` shell 块 | `sources/run_dp_template_prefill_node2.sh` |
| ... | 按顺序提取所有 | `sources/run_dp_template_prefill_node{N}.sh` |

### Decode 节点模板脚本

进入对应机型的 Tab-item 区域，提取所有 `kv_role: kv_consumer` 的 shell 块：

| 项目 | 提取位置 | 保存为 |
|---|---|---|
| Decode node 1 | 第一个 `kv_role: kv_consumer` shell 块 | `sources/run_dp_template_decode_node1.sh` |
| Decode node 2 | 第二个 `kv_role: kv_consumer` shell 块 | `sources/run_dp_template_decode_node2.sh` |
| ... | 按顺序提取所有 | `sources/run_dp_template_decode_node{N}.sh` |

**注意**：完整提取教程中的所有模板脚本，不做数量匹配验证。用户配置可能与教程样例不一致，步骤5生成时会根据配置选择使用哪些模板。

## MyST Markdown Tab-set 结构

如果文档有 Tab-set：

```markdown
:::::{tab-set}
::::{tab-item} A2 series
... A2 PD 配置（如 4×1P 1×4D） ...
::::
::::{tab-item} A3 series
... A3 PD 配置（如 2P1D） ...
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
├── {model_name}.md                      # 模型教程文档
├── pd_disaggregation_mooncake_multi_node.md # PD分离理论参考（步骤4下载）
├── start_container.sh                   # 容器启动脚本
├── launch_online_dp.py                  # DP 启动脚本
├── run_dp_template_prefill_node*.sh     # Prefill 模板脚本（按教程实际数量）
├── run_dp_template_decode_node*.sh      # Decode 模板脚本（按教程实际数量）
├── load_balance_proxy_server_example.py # 基础版本代理
└── load_balance_proxy_layerwise_server_example.py # 分层版本代理
```

**注意**：模板脚本数量取决于教程文档实际包含的节点配置样例，可能与用户配置不一致。

## 错误处理

### 无法定位章节

**执行终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-06-generate.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 无法定位章节

章节：Prefill-Decode Disaggregation
原因：文档中未找到对应章节标题

工作流已终止。
```

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 文档格式判断结果（新格式/旧格式）
- 提取的脚本列表（完整路径）
- 每个脚本的来源位置（章节、Tab-item）