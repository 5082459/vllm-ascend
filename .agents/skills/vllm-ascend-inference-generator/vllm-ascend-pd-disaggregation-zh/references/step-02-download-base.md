# 步骤 2：下载基础文件

## 目标

下载模型教程文档，为后续支持检查和模板提取做准备。

## 硬性规则

- 使用 Bash 的 curl 命令从 GitHub raw URL 下载。
- 保存下载的源文件不做修改。
- 将文件保存到 `{output_dir}/sources/` 目录。
- 在 README 的「工作流执行日志」部分记录步骤 2 摘要。

## 输出目录命名

格式：`pd_disaggregation_{model_normalized}_{P}p{Np}n_{D}d{Nd}n`

示例：
- `pd_disaggregation_deepseek_v4_pro_1p1n_1d1n`：1个Prefill实例(每实例1节点) + 1个Decode实例(每实例1节点)
- `pd_disaggregation_deepseek_v3_1_2p2n_1d1n`：2个Prefill实例(每实例2节点) + 1个Decode实例(每实例1节点)

**命名规则**：
- 将模型名称转换为小写
- 将 `-` 和 `.` 替换为 `_`
- 移除重复的下划线
- `{P}` = Prefill 实例数量
- `{Np}` = 每个Prefill实例的节点数 (nodes_per_prefill_instance)
- `{D}` = Decode 实例数量
- `{Nd}` = 每个Decode实例的节点数 (nodes_per_decode_instance)
- 例如：`1p1n_1d1n` 表示 1个Prefill实例×1节点 + 1个Decode实例×1节点

## URL 模板

将 `{version_tag}` 替换为映射的分支或标签，优先尝试 release 分支，再是 tag。将 `{model_name}` 替换为用户的模型名称。

| 类型 | URL 模板 | 保存为 |
|---|---|---|
| 模型教程 | `https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/models/{model_name}.md` | `sources/{model_name}.md` |

## 下载命令

### 创建输出目录

```bash
mkdir -p "{output_dir}/sources"
```

### 下载模型教程

```bash
curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/models/{model_name}.md" -o "{output_dir}/sources/{model_name}.md"
```

## 下一步

下载完成后，执行步骤 3 检查模型是否支持所选部署模式。

**注意**：PD分离模式的额外文件（代理脚本、launch_online_dp.py）将在步骤 4 下载。

## 错误处理

如果下载失败（curl 返回错误、文件不存在、网络超时等）：

1. 检查 URL 是否正确（版本映射）。
2. 检查网络连接是否正常。
3. 如果下载失败，**执行终止流程**：

**终止流程**（必须按顺序执行）：
1. 输出失败消息给用户
2. **停止尝试其他下载方法**（如 WebFetch、读取本地文件等）
3. **停止读取后续步骤文件**（step-03-support-check.md ~ step-08-readme.md）
4. **停止执行任何脚本生成操作**
5. 工作流终止，技能执行结束

**失败消息模板**：

```
❌ 步骤 2 下载失败 - 无法获取模型教程文档

URL: {actual_url}
原因: 网络连接失败 / 文件不存在 / 版本映射错误

解决方案：
1. 检查网络连接是否正常
2. 确认版本号是否正确（当前版本: {version}）
3. 确认模型名称是否支持（当前模型: {model_name}）

工作流已终止，无法继续生成部署脚本。
```

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 下载的文件 URL
- 下载时间戳