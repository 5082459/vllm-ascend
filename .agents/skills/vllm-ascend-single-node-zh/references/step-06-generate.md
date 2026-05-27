# 步骤 5：生成部署树

## 目标

从 sources 目录拷贝脚本并生成可运行的部署包结构。

## 前置条件

**必须先完成步骤 4**，确保以下文件存在于 `{output_dir}/sources/` 目录：

| 文件 | 必须 | 来源 |
|------|------|------|
| `{model_name}.md` | ✓ | 步骤 2 |
| `run_single_node.sh` | ✓ | 步骤 4 |
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
- 修改点必须明确，使用占位符标记需要用户手动修改的内容。
- **当 parallel_config_mode = "使用模板配置" 时，不修改 DP/TP/EP 参数，保持模板原值。**
- **当 parallel_config_mode = "自定义并行配置" 时，根据用户选择修改 DP/TP/EP 参数。**
- 在 README 的「工作流执行日志」部分记录步骤 5 摘要。

## 输出目录命名

格式：`single_node_{model_normalized}`

示例：`single_node_deepseek_v3_1`

**名称规范化**：
- 将模型名称转换为小写
- 将 `-` 和 `.` 替换为 `_`
- 移除重复的下划线

## 目录结构

```text
{output_dir}/
├── sources/
│   ├── {model_name}.md
│   ├── run_single_node.sh
│   └── start_container.sh
├── node/
│   ├── start_container.sh
│   └── run_serve.sh
└── README.md
```

## 生成步骤

### 步骤 1：拷贝容器脚本

- 来源：`sources/start_container.sh`
- 目标：`node/start_container.sh`
- 修改点：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `{model_path}` | 用户提供的模型路径 | 模型权重目录 |
| `{extra_mounts}` | 用户提供的挂载目录 | 额外挂载，无则删除此行 |
| `--shm-size=1g` | `--shm-size=512g` | 大模型需要更大共享内存 |

### 步骤 2：拷贝启动脚本

- 来源：`sources/run_single_node.sh`
- 目标：`node/run_serve.sh`

**修改点取决于 parallel_config_mode：**

#### 当 parallel_config_mode = "使用模板配置" 时

**不修改 DP/TP/EP 参数**，仅修改以下内容：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | `<LOCAL_IP>` | 占位符，用户部署时替换 |

**DP/TP/EP 参数保持模板原值不变。**

#### 当 parallel_config_mode = "自定义并行配置" 时

修改以下内容：

| 占位符 | 替换为 | 说明 |
|---|---|---|
| `/path_to_weight/{model_name}` | 用户提供的模型路径 | vllm serve 模型路径 |
| `{nic_name}` | 用户提供的网卡名称 | 网络通信网卡 |
| `{local_ip}` | `<LOCAL_IP>` | 占位符，用户部署时替换 |
| `--data-parallel-size {dp_size}` | 用户选择的 dp_size | 数据并行大小 |
| `--tensor-parallel-size {tp_size}` | 用户选择的 tp_size | 张量并行大小 |

**DP 自动计算逻辑**：
- 当 dp_size = "自动计算" 时：`dp_size = 单机卡数 / tp_size`
- 单机卡数：A3 = 16，A2 = 8

**EP 配置**：
- 当 enable_ep = "不启用" 时：不添加 `--enable-expert-parallel` 参数
- 当 enable_ep = "启用" 时：添加 `--enable-expert-parallel` 参数

## 日志条目

在 README 的「工作流执行日志」部分记录：

- 步骤状态
- 生成的目录结构
- 各目录文件数量
- parallel_config_mode 值
- 当使用模板配置时：记录"保持模板 DP/TP/EP 参数不变"
- 当自定义配置时：关键参数值 `dp_size`, `tp_size`, `enable_ep`
- 修改点列表