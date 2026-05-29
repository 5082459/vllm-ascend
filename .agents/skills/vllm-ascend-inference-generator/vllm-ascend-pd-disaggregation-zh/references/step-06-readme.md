# 步骤 6：编写 README

## 目标

把贯穿步骤 1-5 收集到的参数、计算结果、执行日志渲染成一份 `README.md`。

## 关键规则

- 渲染的起点是 [`assets/readme-template.md`](../assets/readme-template.md)，**不要从零写**。该模板里已经包含所有固定文案（Mooncake 安装命令、hccn_tool 检查命令、kv_port 端口表、代理类型对比等）。
- 模板里 `{xxx}` 形式的占位符替换为本次执行的实际参数。
- 模板里 `[[节循环 NAME]] ... [[结束 NAME]]` 标记为循环段，按节点逐行展开。
- README 中表格里的 `kv_port` / `engine_id` / `dp_rank_start` 必须从步骤 4 生成的实际脚本（或 `.pd_plan.json`）中读取，不要重新算一遍——独立公式与实际脚本之间出现漂移会让用户困惑。

## 渲染流程

1. **复制模板**到输出目录：
   ```bash
   cp assets/readme-template.md {output_dir}/README.md
   ```

2. **替换标量占位符**（用 Edit 工具）：

   | 占位符 | 来源 |
   |---|---|
   | `{model_name}` | step-01 |
   | `{version}` | step-01 |
   | `{machine_type}` | step-01 |
   | `{cards_per_machine}` | 16 (A3) / 8 (A2) |
   | `{model_path}` / `{extra_mounts}` / `{nic_name}` | step-01 |
   | `{prefill_instances}` / `{decode_instances}` | step-01 |
   | `{nodes_per_prefill}` / `{nodes_per_decode}` | step-01 |
   | `{prefill_tp_size}` / `{decode_tp_size}` | step-04 计算 |
   | `{prefill_dp_size}` / `{decode_dp_size}` | step-04 计算 |
   | `{proxy_type_label}` | "基础版本" / "分层版本" |
   | `{proxy_ip}` | step-01 |
   | `{fetch_timestamp}` / `{generation_timestamp}` | 当前时间 |

3. **展开循环段**：

   `[[节循环 PREFILL_NODE_TABLE]]` 段：把模板里那一行表格行（含 `P{instance}N{node}` 等占位符）按所有 Prefill 节点重复，每行替换成实际值。`DECODE_NODE_TABLE` 同理。

   循环数据来自 step-04 的 `.pd_plan.json` 中 `prefill_nodes` / `decode_nodes` 数组。

4. **处理条件段**：

   `[[条件 NAME]] ... [[结束 NAME]]` 标记的段按 step-01 的输入决定保留或删除整段：

   | 条件 | 保留段当且仅当 |
   |---|---|
   | `HAS_EXTRA_MOUNTS` | step-01 的 `extra_mounts` 既非"无"也非空 |

   保留时：去掉 `[[条件 NAME]]` 与 `[[结束 NAME]]` 两行，中间内容继续走标量占位符替换。
   删除时：把 `[[条件 NAME]]` 与 `[[结束 NAME]]` 之间的整段（含两个标记行）一起删掉。

5. **填充工作流执行日志**：

   把步骤 1-5 各自向 README 追加的日志条目合成模板里的 `{stepN_summary}` / `{stepN_timestamp}` 字段。

6. **删除模板的使用说明注释**：模板顶部 `<!-- 模板使用说明... -->` 块在最终 README 里要去掉。

7. **可选**：渲染完成后再用 Read 看一遍，搜剩余的 `{...}` 占位符——理论上应该一个不剩。`<N>` / `<M>` 这类尖括号占位是给读者看的路径模式，不是替换目标，跳过即可。

## 章节内容来源

模板已经把章节文案写好。各步骤只需要确保对应数据可用：

| 章节 | 数据来源 |
|---|---|
| Deployment Overview | step-01 参数 |
| Hardware and Software Requirements | step-01 + step-04 计算 |
| Image Information / Container Startup | step-01 + step-04 替换结果 |
| Source File Origins | step-02 下载日志 |
| Startup Sequence | 固定文案 |
| PD Disaggregation Notes | 固定文案 |
| Proxy Configuration | 固定文案 + step-04 节点表 |
| Configuration Change Guide | step-01 替换值 |
| Testing and Validation | step-01 `proxy_ip` + `model_name` |
| Workflow Execution Log | step-1~5 各自追加的日志 |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 模板渲染情况（替换的占位符数量、循环段行数）
- 检查渲染后是否仍有 `{...}` 残留
