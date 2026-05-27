# 步骤 2：下载基础文件

## 目标

下载模型教程文档，为后续支持检查和模板提取做准备。

## 硬性规则

- 使用 Bash 的 curl 命令从 GitHub raw URL 下载。
- 保存下载的源文件不做修改。
- 将文件保存到 `{output_dir}/sources/` 目录。
- 在 README 的「工作流执行日志」部分记录步骤 2 摘要。

## 输出目录命名

格式：`single_node_{model_normalized}`

示例：`single_node_deepseek_v3_1`

**名称规范化**：
- 将模型名称转换为小写
- 将 `-` 和 `.` 替换为 `_`
- 移除重复的下划线

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