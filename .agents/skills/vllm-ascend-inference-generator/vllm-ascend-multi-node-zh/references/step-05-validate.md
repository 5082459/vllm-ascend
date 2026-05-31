# 步骤 5：验证一致性

## 目标

确保步骤 4 生成的部署树在结构和参数上自洽。任一项失败 → [失败终止协议](../SKILL.md#失败终止协议)。

## 关键规则

- 先验证 sources/ 完整，再验证目录结构，最后验证参数。
- 用 Glob 看文件是否存在；用 Grep 看脚本里的关键字段；自定义模式下用 Python 比对 `.deploy_plan.json` 与生成脚本。

## 5.1 sources/ 完整性

| 文件 | 必需 |
|---|---|
| `sources/{model_name}.md` | ✓ |
| `sources/start_container.sh` | ✓ |
| `sources/run_node0.sh` | ✓ |
| `sources/run_node1.sh` | ✓ |

任一缺失：

```text
❌ 步骤 5 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

## 5.2 输出目录结构

按 `node_count` 推算预期数量：

- 共 `node_count` 个 `node{N}/` 目录
- 每个 `node{N}/` 内含 `start_container.sh` 和 `run_serve.sh`

校验失败时输出实际 vs 期望后终止。

## 5.3 参数一致性

通用检查（两种模式都做）：

| 检查项 | 方法 | 期望 |
|---|---|---|
| Node 0 无 headless | Grep `node0/run_serve.sh` | 不含 `--headless` |
| Node N 有 headless（N≥1） | Grep `nodeN/run_serve.sh` | 含 `--headless` |
| `--data-parallel-address` 一致 | Grep 所有节点 | 全部为 `$node0_ip`（引用脚本头部变量） |
| `--data-parallel-rpc-port` 一致 | Grep | 全部 `13389` |
| 模型路径已替换 | Grep `{model_path}` | 存在；不再出现 `/path_to_weight` |

仅当 `parallel_config_mode = "自定义并行配置"` 时追加：

| 检查项 | 方法 | 期望 |
|---|---|---|
| `--tensor-parallel-size` | Grep 所有节点 | 全部 = 用户 `tp_size` |
| `--data-parallel-size` | Grep 所有节点 | 全部 = plan.dp_size_total |
| `--data-parallel-size-local` | Grep 所有节点 | 全部 = plan.dp_size_local |
| `--data-parallel-start-rank` | Grep 各节点 | node{N} = N × dp_size_local |
| `--enable-expert-parallel` | Grep | `enable_ep="启用"` 时存在；否则不存在 |

## 5.4 plan ↔ 脚本一致性（自定义模式推荐）

如果步骤 4.1 生成了 `.deploy_plan.json`，从中读出每个节点的 `dp_rank_start`、`dp_size_local`、`dp_size_total`，再 Grep 对应 `run_serve.sh`。任一字段不匹配即报错——这是发现"算对了但没替换上"这类 bug 的最直接方式。

## 失败输出格式

结构错误：

```text
❌ 文件结构验证失败

缺失文件：{path}
预期节点数：{expected_count}
实际节点数：{actual_count}
```

参数错误：

```text
❌ 参数一致性验证失败

检查项：{check_item}
文件：{path}
预期：{expected}
实际：{actual}
```

任一失败即按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 5.1 / 5.2 / 5.3 / 5.4 各部分的检查项与结果
- 不一致项（如有）
