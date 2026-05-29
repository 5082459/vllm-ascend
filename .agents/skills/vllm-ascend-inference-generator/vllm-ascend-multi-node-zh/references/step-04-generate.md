# 步骤 4：生成部署树

## 目标

把 `sources/` 中的源文件落到最终部署目录结构里，完成所有占位符替换、各节点参数计算。

## 前置条件

`sources/` 必须包含以下文件，否则按[失败终止协议](../SKILL.md#失败终止协议)结束：

| 文件 | 来源 |
|---|---|
| `{model_name}.md` | 步骤 2 |
| `start_container.sh` | 步骤 3 |
| `run_node0.sh` | 步骤 3 |
| `run_node1.sh` | 步骤 3 |

如果 `node_count > 教程节点数`，缺失的 `run_node{N}.sh` 在 4.3 中以 `run_node1.sh` 为模板复制——这是教程作者的常见做法，所有非 0 号节点共用同一份模板。

失败提示：

```text
❌ 步骤 4 前置条件未满足

缺少文件：{missing_file}
原因：步骤 2 或步骤 3 未完成
```

## 关键规则

- 拷贝文件用 Bash `cp`；改字符串用 Edit 工具。
- 输出目录命名见 [SKILL.md「输出目录命名」](../SKILL.md#输出目录命名)。
- 并行参数策略见 [SKILL.md「并行参数策略」](../SKILL.md#并行参数策略)。
- **自定义并行配置**模式下的 `dp_size_local`、`dp_size_total`、各节点 `dp_rank_start` 一律由 [`scripts/compute_multi_node_params.py`](../scripts/compute_multi_node_params.py) 一次算出，不要在生成过程中临时算。

## 目录结构

```text
{output_dir}/
├── sources/                    # 步骤 2/3 产出，保持不动
├── node0/
│   ├── start_container.sh
│   └── run_serve.sh
├── node1/
│   ├── start_container.sh
│   └── run_serve.sh
├── node{N}/                    # 按 node_count 展开
│   └── ...
└── README.md                   # 步骤 6 写入
```

## 4.1 计算参数（自定义模式才需要）

仅当 `parallel_config_mode = "自定义并行配置"`：

```bash
python scripts/compute_multi_node_params.py \
  --machine-type {A3|A2} \
  --node-count {node_count} \
  --tp-size {tp_size} \
  --node-ips {node0_ip} {node1_ip} ... \
  --output {output_dir}/.deploy_plan.json
```

得到的 `.deploy_plan.json` 里包含 `dp_size_local`、`dp_size_total`、每节点 `dp_rank_start` 与 `headless` 标记。后续替换全部用这份 plan，不要再手算。

> 把 plan 落到磁盘是为了让步骤 5（验证）可以做"plan 与生成脚本一致"的对比。

> **使用模板配置时跳过此步**——保留模板里的 DP/TP/EP，不动公式。

## 4.2 生成 node{N}/start_container.sh

各节点的 start_container.sh 内容相同：

```bash
for N in 0 1 ... node_count-1; do
  cp sources/start_container.sh node${N}/start_container.sh
done
```

用 Edit 工具替换：

| 原始 | 替换为 | 说明 |
|---|---|---|
| `-v <宿主机路径>:/root/.cache` | `-v {model_path}:{model_path}` | 容器内外路径一致 |
| 无额外挂载行 | 在模型挂载行后追加 `-v {extra_mounts}:{extra_mounts}` | 用户选择"无额外挂载"时跳过 |

## 4.3 生成 node{N}/run_serve.sh

模板选择规则：

- `N == 0`：使用 `sources/run_node0.sh`
- `N >= 1`：使用 `sources/run_node{N}.sh`，如不存在则回退到 `run_node1.sh`

```bash
cp sources/run_node{template_idx}.sh node${N}/run_serve.sh
```

通用替换（两种 parallel_config_mode 都要做）：

| 占位符 | 替换为 | 来源 |
|---|---|---|
| `/path_to_weight/{model_name}` 或 `/root/.cache/{model_name}` | `{model_path}` | step-01 |
| `{nic_name}` | 用户输入 | step-01 |
| `{local_ip}` | 当前节点 IP（`node{N}_ip`） | step-01 |
| `{node0_ip}` | Node 0 的 IP | step-01 |

仅当 `parallel_config_mode = "自定义并行配置"`，按 plan 替换：

| 占位符 | 替换为 | 来源 |
|---|---|---|
| `--data-parallel-size {dp_size_total}` | plan.dp_size_total | 4.1 |
| `--data-parallel-size-local {dp_size_local}` | plan.dp_size_local | 4.1 |
| `--data-parallel-address` | `<NODE0_IP>` 占位符 | 用户部署时再替换为实际 IP |
| `--data-parallel-rpc-port` | `13389` | 默认值 |
| `--data-parallel-start-rank` | plan.nodes[N].dp_rank_start | 4.1 |
| `--tensor-parallel-size {tp_size}` | 用户值 | step-01 |
| `--enable-expert-parallel` 行 | `enable_ep="启用"` 时保留/添加；否则删除 | step-01 |

Node 0 vs Node N 的差异：

- **Node 0**：不带 `--headless`
- **Node N（N >= 1）**：带 `--headless`

## 日志条目

向 README「Workflow Execution Log」追加：
- 步骤状态
- 自定义模式下 `.deploy_plan.json` 的关键字段（dp_size_local、dp_size_total、各节点 dp_rank_start）
- 各节点目录与文件清单
- 模式标记（使用模板 / 自定义）
