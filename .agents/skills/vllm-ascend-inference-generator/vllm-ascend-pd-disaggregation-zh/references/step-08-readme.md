# 步骤 8：编写 README

## 目标

为生成的 PD分离部署包编写 README.md 文档。

## 硬性规则

- 包含所有必需章节。
- 在「工作流执行日志」部分记录完整的执行过程。
- 提供清晰的 Prefill → Decode → Proxy 启动顺序。
- 详细说明代理参数配置。
- **README 中的参数表格必须与实际脚本内容一致**：IP 配置表中的 kv_port、engine_id、dp_rank_start 等参数值必须从步骤 6 生成的实际脚本文件中读取，不得使用独立公式重新计算。

## 必需章节

| 章节 | 必需内容                                       |
|---|--------------------------------------------|
| Deployment Overview | PD分离架构描述                                   |
| Hardware and Software Requirements | 机型、卡数、P/D实例数、节点数                           |
| Image Information | 镜像名称和来源                                    |
| Container Startup Instructions | 启动方法和参数说明                                  |
| Source File Origins | 获取时间戳、URL、版本信息                             |
| Startup Sequence | Prefill → Decode → Proxy 启动顺序              |
| PD Disaggregation Notes | Mooncake 依赖、多节点通信验证                        |
| Proxy Configuration | 多节点通信环境验证、kv_port 配置指南、代理类型区别、Prefill 预热说明 |
| Configuration Change Guide | 占位符值和修改说明                                  |
| Testing and Validation | 测试命令和验证方法                                  |
| Workflow Execution Log | 完整执行记录                                     |

## 章节内容模板

### Deployment Overview

```markdown
## Deployment Overview

**部署模式**：Prefill-Decode 分离部署

**架构说明**：Prefill 实例处理预填充阶段，Decode 实例处理解码阶段，代理负责负载均衡和 KV Cache 传输。

**配置**：
- Prefill 实例数：{prefill_instances}
- Decode 实例数：{decode_instances}
- 每实例节点数：{nodes_per_instance}
```

### Startup Sequence

```markdown
## Startup Sequence

**重要**：必须按 Prefill → Decode → Proxy 顺序启动。

1. 启动所有 Prefill 实例节点
   cd prefill/instance{N}/node{M}
   ./start_container.sh
   ./start_serve.sh

2. 启动所有 Decode 实例节点
   cd decode/instance{N}/node{M}
   ./start_container.sh
   ./start_serve.sh

3. 启动代理
   cd proxy
   ./start_proxy.sh
```

### PD Disaggregation Notes

```markdown
## PD Disaggregation Notes

### Mooncake 依赖

PD 分离模式依赖 Mooncake 进行 KV Cache 传输，需在容器内安装：

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

PD 分离要求所有节点的 NPU 通过 RDMA 互联。部署前需在每个节点上执行以下验证，结果必须全部为 `success` 且状态为 `UP`：

```bash
# 检查链路状态
for i in {0..7}; do hccn_tool -i $i -link -g ; done
# 检查网络健康
for i in {0..7}; do hccn_tool -i $i -net_health -g ; done
# 检查 NPU IP（A3 用 -vnic，A2 用 -ip）
for i in {0..7}; do hccn_tool -i $i -ip -g; done
# 跨节点 PING 测试（替换 x.x.x.x 为对端 NPU IP）
for i in {0..7}; do hccn_tool -i $i -ping -g address x.x.x.x; done
# 检查 TLS 配置一致性
for i in {0..7}; do hccn_tool -i $i -tls -g ; done | grep switch
```

> **注意**：A3 机型卡数范围为 `{0..15}`，且需确认 `/etc/hccn.conf` 已挂载到容器内。

> 完整理论参考见 `sources/pd_disaggregation_mooncake_multi_node.md`。

### Proxy Configuration

```markdown
## Proxy Configuration

### kv_port 配置指南

Mooncake 使用 AscendDirectTransport 进行 RDMA 数据传输，会随机分配 `[20000, 20000 + npu_per_node × 1000)` 范围内的端口。如果 `kv_port` 与此范围重叠，可能出现端口冲突。

| 机型 | 卡数 | 保留端口范围 | 建议 kv_port |
|---|---|---|---|
| A2 | 8 | 20000 - 27999 | ≥ 28000 |
| A3 | 16 | 20000 - 35999 | ≥ 36000 |

> **注意**：若启动时出现 `zmq.error.ZMQError: Address already in use`，通常是 kv_port 与 AscendDirectTransport 随机端口冲突，请增大 kv_port 值。

### 代理类型区别

| 类型 | kv_connector | 路由方向 | 适用场景 |
|---|---|---|---|
| 基础版本 | MooncakeConnector | P → D | 简单轮询 |
| 分层版本 | MooncakeLayerwiseConnector | D → P（按需） | 动态实例管理 |

### Prefill 预热说明

Prefill 节点的部分 NPU 算子需要若干轮预热才能达到最佳性能，建议在性能测试前先发送若干请求预热服务。

### hosts/ports 参数

**计算规则**：
- hosts: 每节点 IP 重复 dp_size_local 次
- ports: 7100 到 7100+dp_size_local-1，每节点重复

**示例**（2P1D，A3，dp_size_local=16）：

```text
prefiller_hosts = "P1N1_IP ×16 P2N1_IP ×16"
prefiller_ports = "7100-7115 (重复2次)"
decoder_hosts = "D1N1_IP ×16"
decoder_ports = "7100-7115"
```
```

### Configuration Change Guide

```markdown
## Configuration Change Guide

### 配置说明

| 参数 | 说明 |
|---|---|
| {model_path} | 模型权重路径 |
| {nic_name} | 网络通信网卡名称 |

**注意**：代理的 hosts 参数已使用用户输入的实际 IP 地址生成。
```

### Workflow Execution Log

```markdown
## Workflow Execution Log

| 步骤 | 状态 | 时间戳 | 摘要 |
|---|---|---|---|
| 1. 收集参数 | ✅ 完成 | {timestamp} | {summary} |
| 2. 下载基础文件 | ✅ 完成 | {timestamp} | {summary} |
| 3. 检查部署模式支持 | ✅ 完成 | {timestamp} | {summary} |
| 4. 下载文件 | ✅ 完成 | {timestamp} | {summary} |
| 5. 提取模板 | ✅ 完成 | {timestamp} | {summary} |
| 6. 生成部署树 | ✅ 完成 | {timestamp} | {summary} |
| 7. 验证一致性 | ✅ 完成 | {timestamp} | {summary} |
| 8. 编写 README | ✅ 完成 | {timestamp} | {summary} |

**生成时间**：{generation_timestamp}
```

## 日志条目格式

每个步骤的摘要应包含：

- 步骤 1：收集的参数列表、计算后的 DP 参数
- 步骤 2：下载的模型教程
- 步骤 3：支持检查结果
- 步骤 4：下载的额外文件列表和 URL
- 步骤 5：提取的脚本列表、文档格式判断结果
- 步骤 6：生成的目录结构、P/D节点数量、engine_id/kv_port 值
- 步骤 7：验证检查项和结果
- 步骤 8：README 编写完成