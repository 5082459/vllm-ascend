# 步骤 3：检查部署模式支持

## 目标

验证模型教程是否支持单节点部署模式。

## 硬性规则

- 读取 `{output_dir}/sources/{model_name}.md` 检查章节标题。
- 如果章节不存在，**立即终止工作流**：
  1. 输出失败消息给用户
  2. **停止读取后续步骤文件**（step-05-extract.md ~ step-08-readme.md）
  3. **停止执行任何脚本生成操作**
  4. 工作流终止，技能执行结束
- 在 README 的「工作流执行日志」部分记录步骤 3 摘要。

## 部署模式章节标题映射

| 模式 | 章节标题 | 搜索正则 |
|---|---|---|
| single-node | `### Single-node Deployment` 或 `## Single-node Deployment` | `Single-node Deployment` |

## 检查方法

### 读取模型教程

使用 Read 工具读取 `{output_dir}/sources/{model_name}.md`。

### 搜索章节标题

使用 Grep 工具搜索章节标题关键词：

```bash
grep -E "Single-node Deployment" "{output_dir}/sources/{model_name}.md"
```

## 结果处理

### 检查通过

如果找到对应章节标题，继续步骤 4。

### 检查失败

如果未找到对应章节标题，**执行终止流程**：

**终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-05-extract.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

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

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 检查的章节标题
- 检查结果（找到/未找到）