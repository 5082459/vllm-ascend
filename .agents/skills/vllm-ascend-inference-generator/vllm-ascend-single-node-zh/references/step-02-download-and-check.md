# 步骤 2：下载教程并校验支持

## 目标

下载模型教程文档，并立即确认它包含 `Single-node Deployment` 章节——避免在错误的输入上空跑后续步骤。

## 关键规则

- 输出目录命名见 [SKILL.md「输出目录命名」](../SKILL.md#输出目录命名)。
- 用 Bash 的 `curl -L` 从 GitHub raw 下载到 `{output_dir}/sources/`。
- 章节缺失即按[失败终止协议](../SKILL.md#失败终止协议)结束——继续往下走只会得到一个空 `sources/`。

## 2.1 创建目录

```bash
mkdir -p "{output_dir}/sources"
```

## 2.2 下载模型教程

URL 模板（`{version_tag}` 来自 [SKILL.md 版本映射](../SKILL.md#版本映射共享)）：

```bash
curl -L "https://raw.githubusercontent.com/vllm-project/vllm-ascend/{version_tag}/docs/source/tutorials/models/{model_name}.md" \
  -o "{output_dir}/sources/{model_name}.md"
```

> 优先用 `releases/v{version}` 分支；HTTP 404 时再换 `v{version}` 标签重试。

## 2.3 校验章节存在

教程下载完成后，立即用 Grep 验证：

```bash
grep -E "^#+\s*Single-node Deployment" "{output_dir}/sources/{model_name}.md"
```

命中 → 进入步骤 3。
未命中 → 输出下面的失败消息后终止：

```text
❌ 部署模式支持检查失败

模型：{model_name}
vllm-ascend 版本：{version}
请求的部署模式：single-node

此模型在指定版本中不支持单节点部署模式。

建议：
1. 检查模型名称是否正确
2. 尝试切换到其他部署模式
3. 升级或切换 vllm-ascend 版本

工作流已终止。
```

之所以把"下载"和"章节校验"合并到同一步：失败处理路径完全一致——无论是教程根本下不动，还是下到的教程不含 `Single-node Deployment`，下游都没有可用的输入。合在一起避免了"步骤 2 假装成功，到步骤 3 才报错"的虚假进度。

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 下载使用的 `version_tag` 和 URL
- 章节校验结果（找到/未找到）
