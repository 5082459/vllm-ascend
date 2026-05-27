---
name: vllm-ascend-single-node-zh
description: 单节点 vllm-ascend 推理服务部署脚本生成。
---

# 单节点部署技能

## 概述

生成单节点 vllm-ascend 推理服务部署包，适用于快速验证和低延迟场景。

## 使用场景

- 可独立调用：用户明确请求单节点部署
- 可由主技能调用：`vllm-ascend-inference-generator-zh` 根据模式选择调用

## 工作流映射

1. **收集参数**：[步骤 1](references/step-01-inputs.md)
2. **下载基础文件**：[步骤 2](references/step-02-download-base.md)
3. **检查部署模式支持**：[步骤 3](references/step-03-support-check.md)
4. **提取模板**：[步骤 4](references/step-05-extract.md)
5. **生成部署树**：[步骤 5](references/step-06-generate.md)
6. **验证一致性**：[步骤 6](references/step-07-validate.md)
7. **编写 README**：[步骤 7](references/step-08-readme.md)

## 参考文件

- [步骤 1：收集参数](references/step-01-inputs.md)
- [步骤 2：下载基础文件](references/step-02-download-base.md)
- [步骤 3：检查部署模式支持](references/step-03-support-check.md)
- [步骤 4：提取模板](references/step-05-extract.md)
- [步骤 5：生成部署树](references/step-06-generate.md)
- [步骤 6：验证一致性](references/step-07-validate.md)
- [步骤 7：编写 README](references/step-08-readme.md)