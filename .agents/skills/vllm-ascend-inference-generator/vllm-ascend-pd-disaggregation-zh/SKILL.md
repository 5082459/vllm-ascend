---
name: vllm-ascend-pd-disaggregation-zh
description: 当用户要求生成适用于 Ascend 的 vllm-ascend PD分离 / Prefill-Decode Disaggregation / pd-disaggregation 部署脚本、启动脚本、部署配置，或 DeepSeek-V4-Pro、DeepSeek、GLM 的 1P1D prefill/decode/proxy 部署方案时使用。【重要约束】每次调用必须是全新流程，从零开始，禁止继承或应用之前的任何经验或资料，仅使用本次skill调用范围内的references目录信息。
---

# PD分离部署技能

为 vllm-ascend 生成 Prefill-Decode 分离架构的部署包：Prefill 实例、Decode 实例、负载均衡 Proxy。
适用于高并发场景，KV Cache 通过 Mooncake 在 P/D 之间传输。

## 信息边界

每次调用都是独立流程。本次执行允许使用的信息源**只有三类**：

1. 本次会话中读取的 `references/` 与 `assets/` 目录文件
2. 用户在本次请求中提供的参数（包括 prompt、场景文件、AskUserQuestion 回答）
3. 通过 `curl` 实时拉取的 GitHub 官方教程与示例代码

之所以强调这一点：模型教程会随版本演化，参数计算公式也可能调整。任何"凭印象"得到的参数都可能与用户指定的版本不一致，所以宁可重新读、重新拉、重新算。

## 使用场景

- **可独立调用**：用户明确请求 PD 分离部署
- **可由主技能调用**：`vllm-ascend-inference-generator-zh` 在模式选择阶段路由到本 skill

## 工作流

按顺序执行 6 个步骤。任一步骤失败立即触发[失败终止协议](#失败终止协议)。

| 步骤 | 文件 | 产出 | 下一步消费者 |
|---|---|---|---|
| 1. 收集参数 | [step-01-inputs.md](references/step-01-inputs.md) | 全部部署参数（含模型、版本、机型、IP 等） | step-02、step-04 |
| 2. 下载并校验支持 | [step-02-download-and-check.md](references/step-02-download-and-check.md) | `sources/` 全部源文件 | step-03、step-04 |
| 3. 提取模板 | [step-03-extract.md](references/step-03-extract.md) | `sources/start_container.sh`、`sources/run_dp_template_*.sh` | step-04、step-05 |
| 4. 生成部署树 | [step-04-generate.md](references/step-04-generate.md) | `prefill/`、`decode/`、`proxy/` 完整目录 | step-05、step-06 |
| 5. 验证一致性 | [step-05-validate.md](references/step-05-validate.md) | 验证报告（写入日志） | step-06 |
| 6. 编写 README | [step-06-readme.md](references/step-06-readme.md) | `README.md` | — |

辅助资源：
- 公式与端口规则：[references/appendix-pd-resources.md](references/appendix-pd-resources.md)
- 参数确定性计算脚本：[scripts/compute_pd_params.py](scripts/compute_pd_params.py)
- README 模板：[assets/readme-template.md](assets/readme-template.md)

## 全局约定

下面的规则被多个步骤共享，集中放在这里以避免每个步骤再重复一次。

### 输出目录命名

格式：`pd_disaggregation_{model_normalized}_{P}p{Np}n_{D}d{Nd}n`

- `model_normalized`：把模型名转小写，再把 `-` 和 `.` 都替换成 `_`，去掉重复下划线
- `{P}` = Prefill 实例数；`{Np}` = 每个 Prefill 实例的节点数
- `{D}` = Decode 实例数；`{Nd}` = 每个 Decode 实例的节点数

示例：
- `pd_disaggregation_deepseek_v4_pro_1p1n_1d1n`
- `pd_disaggregation_deepseek_v3_1_2p2n_1d1n`

> 该命名被现有测试基线锁定，**不要随意更改**。

### 失败终止协议

任一步骤检测到不可恢复错误时，按下面的顺序执行，不再进入后续步骤：

1. 向用户输出失败消息（步骤内会给出具体模板）
2. 停止读取后续 step 文件
3. 停止任何文件生成、拷贝、写入操作
4. 工作流终止，本次 skill 调用结束

之所以坚持"硬终止"而不是"尽力而为"：PD 分离的脚本之间高度耦合（kv_port、engine_id、dp_rank_start 等参数必须一致），半成品部署包对用户的危害大于"什么都没有"。

### 工作流执行日志

每个步骤完成时，向最终 `README.md` 的「Workflow Execution Log」表格追加一行，包含：状态、时间戳、关键产物或参数摘要。日志的最终渲染由 step-06 完成。

### 版本与代理类型映射（共享）

**版本 → GitHub 引用**

| 用户输入 | GitHub 分支 | GitHub 标签 |
|---|---|---|
| latest | main | — |
| 0.18.0 | releases/v0.18.0 | v0.18.0 |
| 0.17.0 | releases/v0.17.0 | v0.17.0 |

优先使用 `releases/v{version}` 分支；分支不存在时回退到 `v{version}` 标签。

**proxy_type → 代理脚本**

| proxy_type | 代理脚本 |
|---|---|
| 基础版本 | load_balance_proxy_server_example.py |
| 分层版本 | load_balance_proxy_layerwise_server_example.py |

> `kv_connector` 字段一律**保留模板原值**。教程里出现过 `MooncakeConnector` / `MooncakeConnectorV1` / `MooncakeLayerwiseConnector` / `MooncakeHybridConnector` 四种名称，且会随版本继续演化——硬编码替换规则只会让产出与教程脱节。connector 与 proxy 的匹配以教程为准，本 skill 同时拷贝两份 proxy 脚本，部署侧用 `PROXY_TYPE` 切换。详见 [appendix-pd-resources.md](references/appendix-pd-resources.md)。

## 验证与回归

本 skill 已有完整测试基础设施位于 `tests/vllm-ascend-pd-disaggregation-zh/`：

- `trigger/` — 触发测试（skill 是否被正确触发）
- `scenarios/*/baseline/` — 7 个场景的产出基线
- `runs/` — 历史运行记录
- 主入口工具：`tests/tools/run_test.py`

修改本 skill 后，至少跑一遍 `run_test.py` 与基线 diff，避免参数漂移。
