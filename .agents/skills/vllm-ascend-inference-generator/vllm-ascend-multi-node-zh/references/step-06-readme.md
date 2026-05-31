# 步骤 6：编写 README

## 目标

把贯穿步骤 1-5 收集到的参数、计算结果、执行日志渲染成一份 `README.md`。

## 关键规则

- 渲染的起点是 [`assets/readme-template.md`](../assets/readme-template.md)，**不要从零写**。该模板里已经包含所有固定文案（启动顺序、占位符说明、测试命令等）。
- 模板里 `{xxx}` 形式的占位符替换为本次执行的实际参数。
- 模板里 `[[节循环 NODE_TABLE]] ... [[结束 NODE_TABLE]]` 标记为循环段，按节点逐行展开。
- README 中表格里的 `dp_rank_start`、`dp_size_local`、`dp_size_total` 必须从步骤 4 生成的实际脚本（或 `.deploy_plan.json`）中读取，不要重新算一遍——独立公式与实际脚本之间出现漂移会让用户困惑。

## 渲染流程

1. **复制模板**到输出目录：

   ```bash
   cp assets/readme-template.md {output_dir}/README.md
   ```

2. **替换标量占位符**（用 Edit 工具）：

   | 占位符 | 来源 |
   |---|---|
   | `{model_name}` / `{version}` | step-01 |
   | `{machine_type}` / `{cards_per_node}` | step-01（A3=16, A2=8） |
   | `{model_path}` / `{extra_mounts}` / `{nic_name}` | step-01 |
   | `{node_count}` | step-01 |
   | `{parallel_config_mode}` | step-01 |
   | `{dp_size_local}` / `{dp_size_total}` / `{tp_size}` | step-04（自定义模式来自 plan；模板模式填 "模板默认"） |
   | `{enable_ep}` | step-01（仅自定义模式有值） |
   | `{node0_ip}` | step-01（Master 节点 IP，用于 Testing 段 curl 命令） |
   | `{generation_timestamp}` | 当前时间 |

3. **展开循环段**：

   `[[节循环 NODE_TABLE]]` 段：把模板里那一行表格行（含 `node{N}` 等占位符）按所有节点重复，每行替换成实际值（IP、dp_rank_start、headless 标记）。

   循环数据来自 step-04 的 `.deploy_plan.json` 中 `nodes` 数组（自定义模式）；模板模式则用 step-01 的 `node{N}_ip` + 固定 headless 规则（node0=否，其他=是）。

4. **填充工作流执行日志**：把步骤 1-5 各自向 README 追加的日志条目合成模板里的 `{stepN_summary}` / `{stepN_timestamp}` 字段。

5. **删除模板的使用说明注释**：模板顶部 `<!-- 模板使用说明... -->` 块在最终 README 里要去掉。

6. **可选**：渲染完成后再用 Read 看一遍，搜剩余的 `{...}` 占位符——理论上应该一个不剩。

## 章节内容来源

模板已经把章节文案写好。各步骤只需要确保对应数据可用：

| 章节 | 数据来源 |
|---|---|
| Deployment Overview | step-01 参数 |
| Hardware and Software Requirements | step-01 |
| Image Information / Container Startup | step-01 + step-04 替换结果 |
| Source File Origins | step-02 下载日志 |
| Startup Sequence | 固定文案 + node_count |
| Configuration Change Guide | step-01 替换值 + 节点 IP 表 |
| Testing and Validation | step-01 `node0_ip` + `model_name` |
| Workflow Execution Log | step-1~5 各自追加的日志 |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 模板渲染情况（替换的占位符数量、循环段行数）
- 检查渲染后是否仍有 `{...}` 残留
