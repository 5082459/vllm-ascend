# 步骤 5：验证一致性

## 目标

确保步骤 4 生成的部署树在结构和参数上自洽。任一项失败 → [失败终止协议](../SKILL.md#失败终止协议)。

## 关键规则

- 先验证 sources/ 完整，再验证目录结构，最后验证参数。
- 用 Glob 看文件是否存在；用 Grep 看脚本里的关键字段。

## 5.1 sources/ 完整性

| 文件 | 必需 |
|---|---|
| `sources/{model_name}.md` | ✓ |
| `sources/start_container.sh` | ✓ |
| `sources/run_single_node.sh` | ✓ |

任一缺失：

```text
❌ 步骤 5 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

## 5.2 输出目录结构

| 文件 | 必需 |
|---|---|
| `node/start_container.sh` | ✓ |
| `node/run_serve.sh` | ✓ |

校验失败时输出实际 vs 期望后终止。

## 5.3 参数一致性

通用检查（两种模式都做）：

| 检查项 | 方法 | 期望 |
|---|---|---|
| vllm serve 命令完整 | Grep `vllm serve` | 存在 |
| `<LOCAL_IP>` 占位符 | Grep | 存在 |
| 模型路径已替换 | Grep `{model_path}` | 存在；不再出现 `/path_to_weight` |

仅当 `parallel_config_mode = "自定义并行配置"` 时追加：

| 检查项 | 方法 | 期望 |
|---|---|---|
| DP 配置 | Grep `--data-parallel-size` | 等于用户 `dp_size`（自动计算时按 `单机卡数 / tp_size`） |
| TP 配置 | Grep `--tensor-parallel-size` | 等于用户 `tp_size` |
| EP 配置 | Grep `--enable-expert-parallel` | `enable_ep="启用"` 时存在；否则不存在 |
| 无多节点参数 | Grep `--data-parallel-address` | 不存在 |

## 失败输出格式

结构错误：

```text
❌ 文件结构验证失败

缺失文件：{path}
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
- 5.1 / 5.2 / 5.3 各部分的检查项与结果
- 不一致项（如有）
