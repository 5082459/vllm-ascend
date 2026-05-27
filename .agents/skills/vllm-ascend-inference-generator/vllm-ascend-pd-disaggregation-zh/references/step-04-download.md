# 步骤 4：下载文件

## 目标

下载PD分离模式所需的额外文件（代理脚本、launch_online_dp.py）。

## 硬性规则

- 使用 Bash 的 curl 命令从 GitHub raw URL 下载。
- 保存下载的源文件不做修改。
- 将文件保存到 `{output_dir}/sources/` 目录。
- 在 README 的「工作流执行日志」部分记录步骤 4 摘要。

## 文件列表

| 类型 | URL 模板 | 保存为 |
|---|---|---|
| PD分离理论参考 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md` | `sources/pd_disaggregation_mooncake_multi_node.md` |
| 代理脚本基础 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py` | `sources/load_balance_proxy_server_example.py` |
| 代理脚本分层 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_layerwise_server_example.py` | `sources/load_balance_proxy_layerwise_server_example.py` |
| launch_online_dp.py | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/external_online_dp/launch_online_dp.py` | `sources/launch_online_dp.py` |

**注意**：模型教程已在步骤 2 下载。PD分离理论参考文档用于参数配置时的理论依据。

## 下载命令

```bash
curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md" -o "{output_dir}/sources/pd_disaggregation_mooncake_multi_node.md"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_server_example.py" -o "{output_dir}/sources/load_balance_proxy_server_example.py"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/disaggregated_prefill_v1/load_balance_proxy_layerwise_server_example.py" -o "{output_dir}/sources/load_balance_proxy_layerwise_server_example.py"

curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/examples/external_online_dp/launch_online_dp.py" -o "{output_dir}/sources/launch_online_dp.py"
```

## 完成后 sources 目录结构

```text
{output_dir}/sources/
├── {model_name}.md                      # 模型教程文档（步骤 2 下载）
├── pd_disaggregation_mooncake_multi_node.md # PD分离理论参考
├── load_balance_proxy_server_example.py # 基础版本代理
├── load_balance_proxy_layerwise_server_example.py # 分层版本代理
└── launch_online_dp.py                  # DP 启动脚本
```

## 错误处理

如果下载失败：

1. 检查 URL 是否正确（版本映射）。
2. 检查文件是否存在于指定版本。
3. 如果文件不存在，**执行终止流程**：

**终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-05-extract.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 下载的文件列表
- 每个文件的 URL
- 下载时间戳