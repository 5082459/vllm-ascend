---
name: vllm-ascend-inference-generator-zh
description: 当用户请求 vllm-ascend 推理服务部署脚本生成、单节点/多节点/PD分离部署配置、DeepSeek/Qwen/GLM 推理部署、vllm serve 启动脚本生成时使用。【重要约束】每次调用必须是全新流程，从零开始，禁止继承或应用之前的任何经验或资料，仅使用本次skill调用范围内的references目录信息。
---

# vllm-ascend 推理服务部署脚本生成器

## 🚨 核心约束（不可违背）

**每次调用本skill必须是全新流程**：

1. **从零开始**：不继承对话历史中的任何部署经验、参数记忆、生成模式
2. **信息隔离**：仅使用本次skill调用时读取的 `references/` 目录内容
3. **禁止经验引用**：不能说"根据之前..."、"上次生成时..."、"通常做法是..."
4. **独立决策**：所有参数收集、文件下载、模板提取都必须从头执行
5. **无状态执行**：即使相同用户、相同模型，每次调用也视为第一次

**唯一允许的信息来源**：
- 本次调用时读取的 `references/` 目录下的参考文件
- 用户本次请求中明确提供的参数
- 从GitHub官方仓库实时下载的模板文件

**违反约束的行为**：
- ❌ 使用对话历史中的模型参数记忆
- ❌ 应用之前成功生成的脚本模式
- ❌ 假设用户偏好（除非本次明确提供）
- ❌ 跳过步骤（因为"之前做过"）

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