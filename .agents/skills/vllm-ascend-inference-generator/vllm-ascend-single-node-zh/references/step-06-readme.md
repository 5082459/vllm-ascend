# 步骤 6：编写 README

## 目标

把贯穿步骤 1-5 收集到的参数、执行日志渲染成一份 `README.md`。

## 关键规则

- 渲染的起点是 [`assets/readme-template.md`](../assets/readme-template.md)，**不要从零写**。该模板里已经包含所有固定文案（启动顺序、占位符说明、测试命令等）。
- 模板里 `{xxx}` 形式的占位符替换为本次执行的实际参数。

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
   | `{model_path}` / `{extra_mounts}` | step-01 |
   | `{parallel_config_mode}` | step-01 |
   | `{dp_size}` / `{tp_size}` / `{enable_ep}` | step-01（仅自定义模式有值，否则填 "模板默认"） |
   | `{generation_timestamp}` | 当前时间 |

3. **填充工作流执行日志**：把步骤 1-5 各自向 README 追加的日志条目合成模板里的 `{stepN_summary}` / `{stepN_timestamp}` 字段。

4. **删除模板的使用说明注释**：模板顶部 `<!-- 模板使用说明... -->` 块在最终 README 里要去掉。

5. **可选**：渲染完成后再用 Read 看一遍，搜剩余的 `{...}` 占位符——理论上应该一个不剩。

## 章节内容来源

模板已经把章节文案写好。各步骤只需要确保对应数据可用：

| 章节 | 数据来源 |
|---|---|
| Deployment Overview | step-01 参数 |
| Hardware and Software Requirements | step-01 |
| Image Information / Container Startup | step-01 + step-04 替换结果 |
| Source File Origins | step-02 下载日志 |
| Startup Sequence | 固定文案 |
| Configuration Change Guide | step-01 替换值 |
| Testing and Validation | step-01 `model_name` |
| Workflow Execution Log | step-1~5 各自追加的日志 |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 模板渲染情况（替换的占位符数量）
- 检查渲染后是否仍有 `{...}` 残留
