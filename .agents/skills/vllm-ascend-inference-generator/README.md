# vllm-ascend 推理服务部署脚本生成器

## 概述

本技能集用于生成 vllm-ascend 推理服务部署包，支持三种部署模式：

- **单节点部署**：适用于快速验证和低延迟场景
- **多节点部署**：适用于大模型和高吞吐场景
- **PD 分离部署**：Prefill-Decode 分离架构，适用于高并发场景，支持 KV Cache 传输优化

## 技能架构

```
vllm-ascend-inference-generator-zh (主技能)
├── vllm-ascend-single-node-zh (单节点部署)
├── vllm-ascend-multi-node-zh (多节点部署)
└── vllm-ascend-pd-disaggregation-zh (PD分离部署)
```

### 主技能 (vllm-ascend-inference-generator-zh)

负责模式选择和路由，收集部署模式参数后调用对应的子技能。

**触发条件**：用户请求 vllm-ascend 推理服务部署脚本生成、单节点/多节点/PD 分离部署配置、DeepSeek/Qwen/GLM 推理部署、vllm serve 启动脚本生成。

### 子技能

| 子技能 | 用途 | 独立调用 |
|--------|------|----------|
| vllm-ascend-single-node-zh | 单节点部署 | 支持 |
| vllm-ascend-multi-node-zh | 多节点分布式部署 | 支持 |
| vllm-ascend-pd-disaggregation-zh | PD 分离部署 | 支持 |

## 工作流

### 主技能工作流

```
模式选择 → 调用子技能
```

主技能仅收集部署模式参数，模型名称、版本和其他参数由子技能收集。

### 子技能工作流

每个子技能遵循统一的 6 步工作流：

```
1. 收集参数 → 2. 下载并校验支持 → 3. 提取模板 → 4. 生成部署树
→ 5. 验证一致性 → 6. 编写 README
```

**核心约束**：每次调用必须是全新流程，从零开始，仅使用本次 skill 范围内的 references 目录信息。任一步骤失败立即触发硬终止协议。

| 步骤 | 产出 | 说明 |
|------|------|------|
| 1. 收集参数 | 部署参数（模型、版本、机型、并行配置等） | 通过交互式问答或预定义参数表获取 |
| 2. 下载并校验支持 | 源文件 + 章节存在性确认 | 从 GitHub 下载模型教程，验证部署模式支持性 |
| 3. 提取模板 | 容器启动脚本、vllm serve 启动脚本模板 | 从教程文档提取 shell 脚本 |
| 4. 生成部署树 | 完整部署目录 | 填充模板参数，生成节点/实例目录 |
| 5. 验证一致性 | 验证报告 | 检查配置参数和脚本一致性 |
| 6. 编写 README | 部署说明文档 | 基于 readme-template.md 生成 |

## PD 分离架构概述

PD 分离（Prefill-Decode Disaggregation）将推理过程拆分为两个独立阶段：

- **Prefill 阶段**：处理 prompt 编码，生成 KV Cache（kv_producer）
- **Decode 阶段**：处理 token 生成，消费 KV Cache（kv_consumer）
- **Proxy**：负载均衡代理，协调请求路由和 KV Cache 传输

```
┌─────────────┐     KV Cache      ┌─────────────┐
│   Prefill   │ ──────────────────▶│   Decode    │
│ (Producer)  │                    │ (Consumer)  │
└─────────────┘                    └─────────────┘
      │                                  │
      │         ┌─────────┐              │
      └─────────│  Proxy  │──────────────│
                │ (1999)  │
                └─────────┘
```

PD 分离的详细参数收集流程、计算公式、KV Connector 类型、输出目录结构和代理配置等，详见子技能 `vllm-ascend-pd-disaggregation-zh` 的 [SKILL.md](vllm-ascend-pd-disaggregation-zh/SKILL.md) 及 `references/` 目录。

## 支持的模型

- DeepSeek 系列
- GLM 系列
- Llama3 系列

## 支持的硬件平台

| 机型 | 卡数 |
|------|------|
| A3 超节点 (Atlas 900 A3) | 16 |
| A2 (Atlas 800 A2) | 8 |

## 使用方式

### 触发主技能

直接请求部署脚本生成，主技能会引导选择部署模式：

```
帮我生成 vllm-ascend 推理部署脚本
```

### 直接调用子技能

明确指定部署模式时，可直接调用对应子技能：

```
生成单节点 vllm-ascend 部署脚本
生成多节点 vllm-ascend 部署脚本
生成 PD 分离 vllm-ascend 部署脚本
```

## 目录结构

```
.agents/skills/vllm-ascend-inference-generator/
├── README.md                                              # 本文件
├── vllm-ascend-inference-generator-zh/
│   ├── SKILL.md                                          # 主技能定义
│   └── references/
│       └── mode-selection.md                             # 模式选择参考
├── vllm-ascend-single-node-zh/
│   ├── SKILL.md                                          # 单节点技能定义
│   ├── assets/
│   │   └── readme-template.md                            # README 模板
│   └── references/
│       ├── step-01-inputs.md                             # 收集参数
│       ├── step-02-download-and-check.md                 # 下载并校验支持
│       ├── step-03-extract.md                            # 提取模板
│       ├── step-04-generate.md                           # 生成部署树
│       ├── step-05-validate.md                           # 验证一致性
│       └── step-06-readme.md                             # 编写 README
├── vllm-ascend-multi-node-zh/
│   ├── SKILL.md                                          # 多节点技能定义
│   ├── assets/
│   │   └── readme-template.md                            # README 模板
│   ├── scripts/
│   │   └── compute_multi_node_params.py                  # 参数确定性计算脚本
│   └── references/
│       ├── step-01-inputs.md                             # 收集参数
│       ├── step-02-download-and-check.md                 # 下载并校验支持
│       ├── step-03-extract.md                            # 提取模板
│       ├── step-04-generate.md                           # 生成部署树
│       ├── step-05-validate.md                           # 验证一致性
│       └── step-06-readme.md                             # 编写 README
└── vllm-ascend-pd-disaggregation-zh/
    ├── SKILL.md                                          # PD分离技能定义
    ├── assets/
    │   └── readme-template.md                            # README 模板
    ├── scripts/
    │   └── compute_pd_params.py                          # 参数确定性计算脚本
    └── references/
        ├── step-01-inputs.md                             # 收集参数
        ├── step-02-download-and-check.md                 # 下载并校验支持
        ├── step-03-extract.md                            # 提取模板
        ├── step-04-generate.md                           # 生成部署树
        ├── step-05-validate.md                           # 验证一致性
        ├── step-06-readme.md                             # 编写 README
        └── appendix-pd-resources.md                      # PD专用参考（公式与端口规则）
```

## 输出产物

生成的部署包包含：

- 启动脚本
- 环境变量配置
- 部署说明文档 (README.md)

## 版本支持

| 版本 | GitHub 分支 | GitHub 标签 |
|------|-------------|--------------|
| latest | main | - |
| 0.18.0 | releases/v0.18.0 | v0.18.0 |
| 0.17.0 | releases/v0.17.0 | v0.17.0 |

优先使用 `releases/v{version}` 分支；分支不存在时回退到 `v{version}` 标签。

## 参考

- [vllm-ascend 官方仓库](https://github.com/vllm-project/vllm-ascend)