---
name: vllm-ascend-inference-generator-zh
description: 当用户请求 vllm-ascend 推理服务部署脚本生成、单节点/多节点/PD分离部署配置、DeepSeek/Qwen/GLM 推理部署、vllm serve 启动脚本生成时使用。
---

# vllm-ascend 推理服务部署脚本生成器

## 概述

本技能为 vllm-ascend 生成可运行的推理服务部署包，支持三种部署模式。主技能负责模式选择和基础验证，具体部署逻辑由子技能执行。

## 工作流

```
模式选择 → 调用子技能
```

### 步骤映射

1. **模式选择**：[模式选择](references/mode-selection.md)
2. **调用子技能**：根据 deployment_mode 调用，子技能内部完成下载和支持检查

### 子技能映射

| 部署模式 | 子技能名称 | Skill 调用 | 说明 |
|---|---|---|---|
| single-node | vllm-ascend-single-node-zh | `skill: "vllm-ascend-single-node-zh"` | 单机部署，快速验证 |
| multi-node | vllm-ascend-multi-node-zh | `skill: "vllm-ascend-multi-node-zh"` | 多机分布式部署 |
| pd-disaggregation | vllm-ascend-pd-disaggregation-zh | `skill: "vllm-ascend-pd-disaggregation-zh"` | Prefill-Decode 分离 |

## 不可违背的规则

- 先收集部署模式，再调用对应子技能。
- 子技能负责下载模型教程和检查支持性。
- 如果子技能判定模型不支持所选部署模式，立即停止。
- 在 README 的「工作流执行日志」部分记录每一步。

## 参考文件

- [模式选择](references/mode-selection.md)