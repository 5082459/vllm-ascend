---
name: vllm-ascend-pd-disaggregation-zh
description: 当用户要求生成适用于 Ascend 的 vllm-ascend PD分离 / Prefill-Decode Disaggregation / pd-disaggregation 部署脚本、启动脚本、部署配置，或 DeepSeek-V4-Pro、DeepSeek、GLM 的 1P1D prefill/decode/proxy 部署方案时使用。
---

# PD分离部署技能

## 概述

生成 Prefill-Decode 分离架构的 vllm-ascend 推理服务部署包，适用于高并发场景，KV Cache传输优化。

## 使用场景

- 可独立调用：用户明确请求 PD 分离部署
- 可由主技能调用：`vllm-ascend-inference-generator-zh` 根据模式选择调用

## 工作流映射

1. **收集参数**：[步骤 1](references/step-01-inputs.md)
2. **下载基础文件**：[步骤 2](references/step-02-download-base.md)
3. **检查部署模式支持**：[步骤 3](references/step-03-support-check.md)
4. **下载文件**：[步骤 4](references/step-04-download.md)
5. **提取模板**：[步骤 5](references/step-05-extract.md)
6. **生成部署树**：[步骤 6](references/step-06-generate.md)
7. **验证一致性**：[步骤 7](references/step-07-validate.md)
8. **编写 README**：[步骤 8](references/step-08-readme.md)

## 参考文件

- [步骤 1：收集参数](references/step-01-inputs.md)
- [步骤 2：下载基础文件](references/step-02-download-base.md)
- [步骤 3：检查部署模式支持](references/step-03-support-check.md)
- [步骤 4：下载文件](references/step-04-download.md)
- [步骤 5：提取模板](references/step-05-extract.md)
- [步骤 6：生成部署树](references/step-06-generate.md)
- [步骤 7：验证一致性](references/step-07-validate.md)
- [步骤 8：编写 README](references/step-08-readme.md)
- [附录：PD专用参考](references/appendix-pd-resources.md)
