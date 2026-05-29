# 步骤 2：下载源文件并校验 PD 分离支持

## 目标

在一个步骤里完成"下载 → 检查能否继续 → 下载剩余文件"，避免把同类下载操作拆成多个 step。

## 关键规则

- 下载使用 Bash 的 `curl -L`；保留原文件不做任何修改。
- 全部输出到 `{output_dir}/sources/`。
- 使用 [SKILL.md「全局约定」](../SKILL.md#全局约定) 中的版本映射拼出 `{version_tag}`。
- 任一阶段失败立即触发[失败终止协议](../SKILL.md#失败终止协议)。

## 阶段 A：下载模型教程

只下载 PD 支持检查所需的最小文件：

| 文件 | URL 模板 | 保存为 |
|---|---|---|
| 模型教程 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/models/{model_name}.md` | `sources/{model_name}.md` |

```bash
mkdir -p "{output_dir}/sources"
curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/models/{model_name}.md" \
     -o "{output_dir}/sources/{model_name}.md"
```

下载失败时的输出：

```text
❌ 步骤 2 下载失败 - 无法获取模型教程文档

URL: {actual_url}
原因: 网络连接失败 / 文件不存在 / 版本映射错误

解决方案：
1. 检查网络连接是否正常
2. 确认版本号是否正确（当前版本：{version}）
3. 确认模型名称是否支持（当前模型：{model_name}）

工作流已终止，无法继续生成部署脚本。
```

输出后按[失败终止协议](../SKILL.md#失败终止协议)结束。

## 阶段 B：检查 PD 分离支持

读取阶段 A 下载的教程，确认包含 PD 分离章节：

| 检查项 | 搜索正则 |
|---|---|
| Prefill-Decode Disaggregation 章节 | `Prefill-Decode Disaggregation` |

```bash
grep -E "Prefill-Decode Disaggregation" "{output_dir}/sources/{model_name}.md"
```

未命中时的输出：

```text
❌ 部署模式支持检查失败

模型：{model_name}
vllm-ascend 版本：{version}
请求的部署模式：pd-disaggregation

此模型在指定版本中不支持 PD 分离部署模式。

建议：
1. 检查模型名称是否正确
2. 尝试其他部署模式（single-node 或 multi-node）
3. 升级或切换 vllm-ascend 版本

工作流已终止。
```

输出后按[失败终止协议](../SKILL.md#失败终止协议)结束。**不要继续阶段 C**。

之所以分两阶段：阶段 C 的四个文件加起来近 1MB，模型不支持 PD 时下载它们是浪费；提前在阶段 B 拦截。

## 阶段 C：下载 PD 专属文件

通过阶段 B 校验后，再下载 PD 分离专属的源文件：

| 文件 | URL 模板 | 保存为 |
|---|---|---|
| PD 分离理论参考 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md` | `sources/pd_disaggregation_mooncake_multi_node.md` |
| 基础版代理脚本 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py` | `sources/load_balance_proxy_server_example.py` |
| 分层版代理脚本 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_layerwise_server_example.py` | `sources/load_balance_proxy_layerwise_server_example.py` |
| launch_online_dp.py | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/external_online_dp/launch_online_dp.py` | `sources/launch_online_dp.py` |

```bash
curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md" \
     -o "{output_dir}/sources/pd_disaggregation_mooncake_multi_node.md"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py" \
     -o "{output_dir}/sources/load_balance_proxy_server_example.py"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_layerwise_server_example.py" \
     -o "{output_dir}/sources/load_balance_proxy_layerwise_server_example.py"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/external_online_dp/launch_online_dp.py" \
     -o "{output_dir}/sources/launch_online_dp.py"
```

任一文件下载失败 → [失败终止协议](../SKILL.md#失败终止协议)。

## 完成后 sources 目录

```text
{output_dir}/sources/
├── {model_name}.md
├── pd_disaggregation_mooncake_multi_node.md
├── load_balance_proxy_server_example.py
├── load_balance_proxy_layerwise_server_example.py
└── launch_online_dp.py
```

`start_container.sh`、`run_dp_template_*.sh` 由步骤 3 从教程中提取，不在此步下载。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 阶段 A/B/C 各自的状态
- 全部下载文件的 URL 与时间戳
- PD 分离章节命中位置
