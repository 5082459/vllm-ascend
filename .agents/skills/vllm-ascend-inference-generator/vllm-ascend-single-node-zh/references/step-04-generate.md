# 步骤 4：生成部署树

## 目标

把 `sources/` 中的源文件落到最终部署目录结构里，完成所有占位符替换。

## 前置条件

`sources/` 必须包含以下文件，否则按[失败终止协议](../SKILL.md#失败终止协议)结束：

| 文件 | 来源 |
|---|---|
| `{model_name}.md` | 步骤 2 |
| `start_container.sh` | 步骤 3 |
| `run_single_node.sh` | 步骤 3 |

失败提示：

```text
❌ 步骤 4 前置条件未满足

缺少文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

## 关键规则

- 拷贝文件用 Bash `cp`；改字符串用 Edit 工具。
- 输出目录命名见 [SKILL.md「输出目录命名」](../SKILL.md#输出目录命名)。
- 并行参数策略见 [SKILL.md「并行参数策略」](../SKILL.md#并行参数策略)——不要在这里再讨论一遍是否覆盖模板。

## 目录结构

```text
{output_dir}/
├── sources/                # 步骤 2/3 产出，保持不动
├── node/
│   ├── start_container.sh
│   └── run_serve.sh
└── README.md               # 步骤 6 写入
```

## 4.1 生成 node/start_container.sh

```bash
cp sources/start_container.sh node/start_container.sh
```

用 Edit 工具替换：

| 原始 | 替换为 | 说明 |
|---|---|---|
| `-v <宿主机路径>:/root/.cache` | `-v {model_path}:{model_path}` | 容器内外路径一致 |
| `--shm-size=1g`（如出现） | `--shm-size=512g` | 大模型推荐共享内存 |
| 无额外挂载行 | 在模型挂载行后追加 `-v {extra_mounts}:{extra_mounts}` | 用户选择"无额外挂载"时跳过 |

## 4.2 生成 node/run_serve.sh

```bash
cp sources/run_single_node.sh node/run_serve.sh
```

通用替换（两种 parallel_config_mode 都要做）：

| 占位符 | 替换为 | 来源 |
|---|---|---|
| `/path_to_weight/{model_name}` 或 `/root/.cache/{model_name}` | `{model_path}` | step-01 |
| `{nic_name}` | 用户输入或保持原值 | step-01 |
| `{local_ip}` | `<LOCAL_IP>` | 占位符，用户部署时再替换 |

仅当 `parallel_config_mode = "自定义并行配置"`：

| 占位符 | 替换为 |
|---|---|
| `--data-parallel-size {dp_size}` | 用户值或自动计算（`单机卡数 / tp_size`） |
| `--tensor-parallel-size {tp_size}` | 用户值 |
| `--enable-expert-parallel` 行 | `enable_ep="启用"` 时保留/添加；否则删除 |

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 生成的目录与文件清单
- `parallel_config_mode` 取值；自定义模式下记录 `dp_size`、`tp_size`、`enable_ep`
