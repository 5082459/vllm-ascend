# vllm-ascend-multi-node-zh 测试入口

## 目录结构

```
tests/vllm-ascend-multi-node-zh/
├── README.md                                    # 本文件
├── trigger/                                     # 触发测试
│   ├── eval.json                                # 触发测试用例定义
│   └── eval-summary.json                        # 触发测试基线结果
├── scenarios/                                   # 测试场景
│   ├── validation.md                            # 验证标准
│   └── deepseek-v3-1/
│       ├── deepseek-v3-1.md                     # 测试输入场景
│       └── baseline/                            # DeepSeek-V3.1 基线
│           ├── node0/                           # Node0 脚本基线
│           ├── node1/                           # Node1 脚本基线
│           ├── sources/                         # 原始模板基线
│           └── README.md
└── runs/                                        # 测试运行记录
    ├── trigger/                                 # 触发测试记录
    └── behavior/                                # 行为测试记录（按时间戳）
```

## 测试执行

### 1. 结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-multi-node-zh
```

通过标准：

```text
Skill is valid!
```

### 2. 触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./vllm-ascend-multi-node-zh \
  --eval-set ./tests/vllm-ascend-multi-node-zh/trigger/eval.json \
  --runs-dir ./tests/vllm-ascend-multi-node-zh/runs/trigger \
  --output-json ./tests/vllm-ascend-multi-node-zh/runs/trigger/latest.json
```

通过标准：

- 多节点正例全部触发
- 单节点、PD 分离和无关请求全部不触发

对比基线：

```bash
diff -u \
  ./tests/vllm-ascend-multi-node-zh/trigger/eval-summary.json \
  ./tests/vllm-ascend-multi-node-zh/runs/trigger/latest.json
```

### 3. 行为测试

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-multi-node-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 300
```

输出产物目录：`./multi_node_deepseek_v3_1_2nodes/`

拷贝输出到场景 output 目录：

```bash
cp -r ./multi_node_deepseek_v3_1_2nodes/* \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output/
```

关键检查点：

- 存在 `sources/`、`node0/` 和 `node1/`
- `node0/run_serve.sh` 不包含 `--headless`
- `node1/run_serve.sh` 包含 `--headless`
- 包含 `--data-parallel-size=4`
- 包含 `--data-parallel-size-local=2`
- `--data-parallel-start-rank` 分别为 `0` 和 `2`
- 两个节点都包含 `--data-parallel-address=<NODE0_IP>`
- `README.md` 包含 `工作流执行日志`

建议检查命令：

```bash
OUTPUT_DIR="./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output"

find $OUTPUT_DIR -maxdepth 2 -type f | sort
grep -n -- "--headless" $OUTPUT_DIR/node1/run_serve.sh
grep -n -- "--data-parallel-size=4" $OUTPUT_DIR/node0/run_serve.sh
grep -n -- "--data-parallel-size-local=2" $OUTPUT_DIR/node0/run_serve.sh
grep -n -- "--data-parallel-start-rank=0" $OUTPUT_DIR/node0/run_serve.sh
grep -n -- "--data-parallel-start-rank=2" $OUTPUT_DIR/node1/run_serve.sh
grep -n -- "--data-parallel-address=<NODE0_IP>" $OUTPUT_DIR/node0/run_serve.sh
grep -n -- "--data-parallel-address=<NODE0_IP>" $OUTPUT_DIR/node1/run_serve.sh
grep -n "工作流执行日志" $OUTPUT_DIR/README.md
if grep -q -- "--headless" $OUTPUT_DIR/node0/run_serve.sh; then
  echo "node0 should not be headless" && exit 1
fi
```

### 4. 对比基线

```bash
diff -rq \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

### 5. 更新基线

当确认输出结果正确后，可更新基线：

```bash
rm -rf ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline/*
cp -r ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output/* \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline/
```