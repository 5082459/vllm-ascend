# 步骤 5：验证一致性

## 目标

确保步骤 4 生成的部署树在结构和参数上自洽。任一项失败 → [失败终止协议](../SKILL.md#失败终止协议)。

## 关键规则

- 先验证 sources/ 完整，再验证目录结构，最后验证参数。
- 用 Glob 看文件是否存在；用 Grep 看脚本里的关键字段；用 Python 比对 `.pd_plan.json` 与生成脚本。

## 5.1 sources/ 完整性

| 文件 | 必需 |
|---|---|
| `sources/{model_name}.md` | ✓ |
| `sources/pd_disaggregation_mooncake_multi_node.md` | ✓ |
| `sources/launch_online_dp.py` | ✓ |
| `sources/load_balance_proxy_server_example.py` | ✓ |
| `sources/load_balance_proxy_layerwise_server_example.py` | ✓ |
| `sources/start_container.sh` | ✓ |
| `sources/run_dp_template_prefill_node*.sh`（≥1） | ✓ |
| `sources/run_dp_template_decode_node*.sh`（≥1） | ✓ |

任一缺失：

```text
❌ 步骤 5 校验失败 - sources 目录文件缺失

缺失文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

之所以把 sources 校验放最前：缺源文件意味着 prefill/decode 目录里的内容也是错的，再往下检查没意义。

## 5.2 输出目录结构

按用户参数推算预期数量：

- `prefill/start_container.sh` 存在
- `prefill/instance{N}/node{M}/{launch_online_dp.py, run_dp_template.sh, start_serve.sh}` 共 `prefill_instances × nodes_per_prefill_instance` 组
- `decode/start_container.sh` 存在
- `decode/instance{N}/node{M}/{launch_online_dp.py, run_dp_template.sh, start_serve.sh}` 共 `decode_instances × nodes_per_decode_instance` 组
- `proxy/{load_balance_proxy_server_example.py, load_balance_proxy_layerwise_server_example.py, start_proxy.sh}` 存在

校验失败时输出实际 vs 期望数量后终止。

## 5.3 参数一致性

| 检查项 | 方法 | 期望 |
|---|---|---|
| Prefill kv_role | Grep run_dp_template.sh | `kv_producer` |
| Decode kv_role | Grep run_dp_template.sh | `kv_consumer` |
| kv_connector 存在 | Grep | 字段存在 |
| 同一 Prefill 实例内 dp_size 一致 | Grep + diff | 实例内一致 |
| 同一 Decode 实例内 dp_size 一致 | Grep + diff | 实例内一致 |
| `--tensor-parallel-size` 存在 | Grep | 字段存在 |
| `kv-transfer-config` 完整 | Grep + JSON 解析 | prefill / decode 子配置都在 |
| 每个节点目录有 launch_online_dp.py | Glob | 存在 |
| engine_id 全局递增 | 收集所有节点 engine_id | 1, 2, ..., N（无跳号） |
| kv_port 不在保留范围 | A3: ≥36000；A2: ≥28000 | 通过 |
| proxy hosts 总数 | 计数 | 等于 `prefill_dp_size + decode_dp_size` |

公式细节见 [appendix-pd-resources.md「PD分离参数计算公式」](appendix-pd-resources.md#pd分离参数计算公式)。

## 5.4 plan ↔ 脚本一致性（推荐）

如果步骤 4 把计算结果写入了 `.pd_plan.json`，从中读出每个节点的 `kv_port`、`engine_id`、`dp_rank_start`，再 Grep 对应 `run_dp_template.sh` / `start_serve.sh`。任一字段不匹配即报错——这是发现"算对了但没替换上"这类 bug 的最直接方式。

## 失败输出格式

结构错误：

```text
❌ 文件结构验证失败

缺失文件：{path}
预期 Prefill instance 数量：{expected_prefill}
实际 Prefill instance 数量：{actual_prefill}
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
