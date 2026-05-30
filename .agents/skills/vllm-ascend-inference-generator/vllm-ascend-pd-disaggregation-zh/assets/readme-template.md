# {model_name} PD分离部署 ({prefill_instances}P{nodes_per_prefill}N + {decode_instances}D{nodes_per_decode}N)

<!--
模板使用说明（不要写到最终 README 里）：
- 形如 {xxx} 的占位符由 step-06 在生成时替换为实际值。
- 形如 [[节循环 SECTION_NAME]] / [[结束 SECTION_NAME]] 的标记是循环段，要按角色或节点重复。
- 工作流执行日志由步骤 1~6 增量写入，最终在 step-06 收尾时统一渲染。
-->

## Deployment Overview

**部署模式**：Prefill-Decode 分离部署

**架构说明**：Prefill 实例处理预填充阶段，Decode 实例处理解码阶段，代理负责负载均衡和 KV Cache 传输。

**配置**：
- Prefill 实例数：{prefill_instances}（每实例 {nodes_per_prefill} 节点）
- Decode 实例数：{decode_instances}（每实例 {nodes_per_decode} 节点）
- 代理类型：{proxy_type_label}

## Hardware and Software Requirements

| 项目 | 值 |
|---|---|
| 机型 | {machine_type} |
| 单机卡数 | {cards_per_machine} |
| Prefill TP | {prefill_tp_size} |
| Decode TP | {decode_tp_size} |
| Prefill DP（全局） | {prefill_dp_size} |
| Decode DP（全局） | {decode_dp_size} |
| vllm-ascend 版本 | {version} |

## Image Information

镜像与启动命令来自模型教程的 Environment Preparation / Installation 章节，已被同步到 `prefill/start_container.sh` 与 `decode/start_container.sh`。

## Container Startup Instructions

按 `prefill/start_container.sh` 与 `decode/start_container.sh` 启动容器。两份脚本内容相同，仅在使用侧区分。

挂载策略：
- 模型权重：`-v {model_path}:{model_path}`（容器内外路径保持一致，便于 vllm serve 直接复用）
[[条件 HAS_EXTRA_MOUNTS]]
- 额外挂载：`-v {extra_mounts}:{extra_mounts}`
[[结束 HAS_EXTRA_MOUNTS]]
- 多节点通信网卡：`{nic_name}`

## Source File Origins

| 文件 | 来源 | 获取时间 |
|---|---|---|
| sources/{model_name}.md | vllm-ascend 模型教程 | {fetch_timestamp} |
| sources/pd_disaggregation_mooncake_multi_node.md | vllm-ascend 特性教程 | {fetch_timestamp} |
| sources/launch_online_dp.py | vllm-ascend 示例代码 | {fetch_timestamp} |
| sources/load_balance_proxy_server_example.py | vllm-ascend 示例代码 | {fetch_timestamp} |
| sources/load_balance_proxy_layerwise_server_example.py | vllm-ascend 示例代码 | {fetch_timestamp} |

完整 URL 见「Workflow Execution Log」中步骤 2 的记录。

## Startup Sequence

**重要**：必须按 Prefill → Decode → Proxy 顺序启动。

1. 在每台 Prefill 节点机器上，先启动容器：
   ```bash
   cd prefill
   ./start_container.sh
   ```
   进入容器后，按实例 / 节点编号启动服务：
   ```bash
   cd instance<N>/node<M>
   ./start_serve.sh
   ```
2. 在每台 Decode 节点机器上，先启动容器：
   ```bash
   cd decode
   ./start_container.sh
   ```
   进入容器后，按实例 / 节点编号启动服务：
   ```bash
   cd instance<N>/node<M>
   ./start_serve.sh
   ```
3. 在代理机上：
   ```bash
   cd proxy
   ./start_proxy.sh
   ```

## PD Disaggregation Notes

### Mooncake 依赖

PD 分离模式依赖 Mooncake 进行 KV Cache 传输，需在每个容器内安装：

```bash
git clone -b v0.3.9 --depth 1 https://github.com/kvcache-ai/Mooncake.git
cd Mooncake
apt-get install mpich libmpich-dev -y
bash dependencies.sh -y
mkdir build && cd build
cmake .. -DUSE_ASCEND_DIRECT=ON
make -j && make install
export LD_LIBRARY_PATH=/usr/local/lib64/python3.11/site-packages/mooncake:$LD_LIBRARY_PATH
```

### 多节点通信环境验证

PD 分离要求所有节点的 NPU 通过 RDMA 互联。部署前需在每个节点上执行物理层和链路层检查，结果必须全部为 `success` 且状态为 `UP`。

检查类目：
- 链路状态、网络健康、远端交换机端口、网络检测 IP、网关配置
- HCCN 配置文件 (`/etc/hccn.conf`) 存在性
- NPU IP 获取（A3 用 `-vnic`，A2 用 `-ip`）
- A3 额外：`superpodid` 与 `SDID`
- 跨节点 PING（A3 用 `hccs_ping`，A2 用 `ping`）
- TLS 配置一致性

> 完整命令清单（机型相关，按 A3 / A2 区分）见 `sources/pd_disaggregation_mooncake_multi_node.md` 的「Verify Multi-Node Communication Environment」章节。本 README 不再复制这些命令——以源文档为准可避免随 vllm-ascend 版本演化产生漂移。

## Proxy Configuration

### kv_port 配置指南

Mooncake 使用 AscendDirectTransport 进行 RDMA 数据传输，会随机分配 `[20000, 20000 + npu_per_node × 1000)` 范围内的端口。如果 `kv_port` 落入此范围，可能出现端口冲突。

| 机型 | 卡数 | 保留端口范围 | 建议 kv_port |
|---|---|---|---|
| A2 | 8 | 20000 - 27999 | ≥ 28000 |
| A3 | 16 | 20000 - 35999 | ≥ 36000 |

> 启动时若出现 `zmq.error.ZMQError: Address already in use`，通常是 kv_port 与 AscendDirectTransport 随机端口冲突，请增大 kv_port 值。

### 代理类型区别

| 代理脚本 | 路由方向 | 适用场景 |
|---|---|---|
| `load_balance_proxy_server_example.py` | P → D | 简单轮询，prefill 推送 KV Cache |
| `load_balance_proxy_layerwise_server_example.py` | D → P（按需） | 动态实例管理，decode 拉取 KV Cache |

> 模板里的 `kv_connector` 字段保留教程原值（教程已出现 `MooncakeConnector`、`MooncakeConnectorV1`、`MooncakeLayerwiseConnector`、`MooncakeHybridConnector` 四种）。两份 proxy 脚本均已拷贝到 `proxy/`，由 `start_proxy.sh` 的 `PROXY_TYPE` 切换。

### Prefill 预热说明

Prefill 节点的部分 NPU 算子需要若干轮预热才能达到最佳性能，建议在性能测试前先发送若干请求预热服务。

### 实际节点参数（来自 step-04 计算）

[[节循环 PREFILL_NODE_TABLE]]
| 节点 | IP | kv_port | engine_id | dp_rank_start |
|---|---|---|---|---|
| P{instance}N{node} | {ip} | {kv_port} | {engine_id} | {dp_rank_start} |
[[结束 PREFILL_NODE_TABLE]]

[[节循环 DECODE_NODE_TABLE]]
| 节点 | IP | kv_port | engine_id | dp_rank_start |
|---|---|---|---|---|
| D{instance}N{node} | {ip} | {kv_port} | {engine_id} | {dp_rank_start} |
[[结束 DECODE_NODE_TABLE]]

> 上表数值来自 `scripts/compute_pd_params.py` 的输出，并已写入对应 `run_dp_template.sh`。如手工修改某个 `kv_port`，请同步更新此表与脚本，避免文档与脚本漂移。

## Configuration Change Guide

下表列出 README 与脚本里出现的关键参数及其当前值。如要换部署目标，修改对应脚本后请同步更新此表。

| 参数 | 当前值 | 出现位置 |
|---|---|---|
| `model_path` | `{model_path}` | start_container.sh、run_dp_template.sh |
| `nic_name` | `{nic_name}` | run_dp_template.sh |
| `extra_mounts` | `{extra_mounts}` | start_container.sh |
| 节点 IP | 见上一节「实际节点参数」表 | run_dp_template.sh、start_proxy.sh |

## Testing and Validation

```bash
# 健康检查
curl -X GET http://{proxy_ip}:1999/v1/models

# 简单推理
curl -X POST http://{proxy_ip}:1999/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "{model_name}", "prompt": "Hello", "max_tokens": 16}'
```

## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | {step1_timestamp} | {step1_summary} |
| 2. 下载与支持检查 | ✅ 完成 | {step2_timestamp} | {step2_summary} |
| 3. 提取模板 | ✅ 完成 | {step3_timestamp} | {step3_summary} |
| 4. 生成部署树 | ✅ 完成 | {step4_timestamp} | {step4_summary} |
| 5. 验证一致性 | ✅ 完成 | {step5_timestamp} | {step5_summary} |
| 6. 编写 README | ✅ 完成 | {step6_timestamp} | {step6_summary} |

**生成时间**：{generation_timestamp}
