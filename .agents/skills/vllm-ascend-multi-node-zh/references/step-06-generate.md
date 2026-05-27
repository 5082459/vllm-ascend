# 步骤 5：生成部署树

## 目标

从 sources 目录拷贝脚本并生成可运行的多节点部署包结构。

## 前置条件

**必须先完成步骤 4**，确保以下文件存在于 `{output_dir}/sources/` 目录：

| 文件 | 必须 | 来源 |
|------|------|------|
| `{model_name}.md` | ✓ | 步骤 2 |
| `run_node0.sh` | ✓ | 步骤 4 |
| `run_node1.sh` | ✓ | 步骤 4 |
| `start_container.sh` | ✓ | 步骤 4 |

**如果前置文件不存在，**执行终止流程**：

**终止流程**（必须按顺序执行）：
1. 输出失败消息
2. **停止读取后续步骤文件**（step-07-validate.md ~ step-08-readme.md）
3. **停止执行任何脚本生成操作**
4. 工作流终止，技能执行结束

```text
❌ 步骤 5 前置条件未满足

缺少文件：{missing_file}
原因：步骤 4 未完成或执行失败

请先执行步骤 4：提取模板脚本
```

## 硬性规则

- 所有脚本先从 sources 目录拷贝，再做修改。
- 使用用户输入的实际 IP 地址，不再使用 IP 占位符。
- 为每个节点生成独立的目录。
- **当 parallel_config_mode = "使用模板配置" 时，不修改 DP/TP/EP 参数，保持模板原值。**
- **当 parallel_config_mode = "自定义并行配置" 时，根据用户选择修改 DP/TP/EP 参数。**
- 在 README 的「工作流执行日志」部分记录步骤 5 摘要。

## 输出目录命名

格式：`multi_node_{model_normalized}_{N}nodes`

示例：`multi_node_deepseek_v3_1_2nodes`

**命名规则**：
- 将模型名称转换为小写
- 将 `-` 和 `.` 替换为 `_`
- 移除重复的下划线
- `{N}` = 部署节点数量 (node_count)
- 例如：`2nodes` 表示 2个节点参与分布式部署

## 目录结构

```text
{output_dir}/
├── sources/
│   ├── {model_name}.md
│   ├── run_node0.sh
│   ├── run_node1.sh
│   ├── run_node2.sh        # 如有
│   ├── run_node3.sh        # 如有
│   └── start_container.sh
├── node0/
│   ├── start_container.sh
│   └── run_serve.sh
├── node1/
│   ├── start_container.sh
│   └── run_serve.sh
├── node2/                   # 如有
│   └── ...
├── node3/                   # 如有
│   └── ...
└── README.md
```

## 生成步骤

### 步骤 1：拷贝容器脚本到每个节点

- 来源：`sources/start_container.sh`
- 目标：`node{N}/start_container.sh`
- 修改点（所有节点相同）：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `{model_path}` | 用户提供的模型路径 | 模型权重目录 |
| `{extra_mounts}` | 用户提供的挂载目录 | 额外挂载 |

### 步骤 2：拷贝启动脚本到对应节点

- Node 0：`sources/run_node0.sh` → `node0/run_serve.sh`
- Node 1：`sources/run_node1.sh` → `node1/run_serve.sh`
- Node 2：`sources/run_node2.sh` → `node2/run_serve.sh`（如有）
- Node 3：`sources/run_node3.sh` → `node3/run_serve.sh`（如有）

### 步骤 3：修改各节点启动脚本

**修改逻辑取决于 parallel_config_mode：**

#### 当 parallel_config_mode = "使用模板配置" 时

**不修改 DP/TP/EP 参数**，仅修改以下内容：

**所有节点通用修改点**：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | 用户输入的节点实际 IP | 当前节点的 IP 地址 |
| `{node0_ip}` | 用户输入的 Node 0 IP | Master 节点 IP |

**Node 0 特有**：
- 无 `--headless` 参数（保持模板原样）
- `--data-parallel-start-rank` 保持模板值

**Node N 特有**：
- 添加 `--headless` 参数
- `--data-parallel-start-rank` 保持模板值

**DP/TP/EP 参数保持模板原值不变。**

#### 当 parallel_config_mode = "自定义并行配置" 时

**Node 0 修改点**：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | 用户输入的 Node 0 IP | 当前节点 IP |
| `{node0_ip}` | 用户输入的 Node 0 IP | Master 节点 IP |
| `--data-parallel-size {dp_size_total}` | 计算后的总 DP 大小 | dp_size_local × node_count |
| `--data-parallel-size-local {dp_size_local}` | 单机卡数 / tp_size | 本地 DP 大小 |
| `--data-parallel-address {node0_ip}` | `<NODE0_IP>` | DP 通信地址 |
| `--data-parallel-rpc-port` | `13389` | 默认 RPC 端口 |
| `--data-parallel-start-rank` | `0` | Node 0 从 0 开始 |
| `--tensor-parallel-size {tp_size}` | 用户选择的 tp_size | 张量并行大小 |
| 无 `--headless` | 保持无此参数 | Master 节点无 headless |

**Node N 修改点**：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | 用户输入的 Node N IP | 当前节点 IP |
| `{node0_ip}` | 用户输入的 Node 0 IP | 指向 Master 节点 IP |
| `--data-parallel-size {dp_size_total}` | 计算后的总 DP 大小 | 与 Node 0 相同 |
| `--data-parallel-size-local {dp_size_local}` | 单机卡数 / tp_size | 与 Node 0 相同 |
| `--data-parallel-address` | `<NODE0_IP>` | 指向 Master 节点 |
| `--data-parallel-rpc-port` | `13389` | 与 Node 0 相同 |
| `--data-parallel-start-rank` | `N × dp_size_local` | 按 dp_size_local 递增 |
| `--tensor-parallel-size {tp_size}` | 用户选择的 tp_size | 张量并行大小 |
| `--headless` | 添加此参数 | Worker 节点需要 headless |

**DP 自动计算逻辑**：
- 当 dp_size = "自动计算" 时：`dp_size_local = 单机卡数 / tp_size`
- 单机卡数：A3 = 16，A2 = 8

**EP 配置**：
- 当 enable_ep = "不启用" 时：不添加 `--enable-expert-parallel` 参数
- 当 enable_ep = "启用" 时：添加 `--enable-expert-parallel` 参数

## 参数计算公式

**当 parallel_config_mode = "自定义并行配置" 时**：

```text
dp_size_total = dp_size_local × node_count
dp_size_local = 单机卡数 / tp_size
dp_rank_start_node_n = n × dp_size_local
```

**当 parallel_config_mode = "使用模板配置" 时**：

使用模板中的 DP/TP 参数，不重新计算。

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 生成的目录结构
- 各目录文件数量
- parallel_config_mode 值
- 当使用模板配置时：记录"保持模板 DP/TP/EP 参数不变"
- 当自定义配置时：关键参数值 `dp_size`, `tp_size`, `enable_ep`, `dp_size_local`, `dp_size_total`
- 各节点的 `dp_rank_start` 值（自定义配置时）