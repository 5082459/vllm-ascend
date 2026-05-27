# vllm-ascend-multi-node-zh 验证流程

## 目标

验证多节点 skill 的三层正确性：

1. `SKILL.md` 结构合法。
2. 多节点请求能触发，其他请求不会误触发。
3. 生成的目录、脚本和 README 符合多节点预期。

## 基线约定

- 触发基线：`./tests/vllm-ascend-multi-node-zh/trigger/eval-summary.json`
- 行为基线：`./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline/`
- 输出目录：`./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output/`
- 运行记录：`./tests/vllm-ascend-multi-node-zh/runs/`

## 第 1 步：结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-multi-node-zh
```

通过标准：

```text
Skill is valid!
```

## 第 2 步：触发测试

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

## 第 3 步：行为测试

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

- 存在 `node0/` 和 `node1/`
- `node0/run_serve.sh` 不包含 `--headless`
- `node1/run_serve.sh` 包含 `--headless`
- 包含 `--data-parallel-size=4`
- 包含 `--data-parallel-size-local=2`
- `--data-parallel-start-rank` 分别为 `0` 和 `2`
- 两个节点都包含 `--data-parallel-address=192.168.1.10`
- `README.md` 包含 `工作流执行日志`
- `README.md` 包含 `启动顺序`

建议检查命令：

```bash
find ./multi_node_deepseek_v3_1_2nodes -maxdepth 2 -type f | sort
grep -n -- "--headless" ./multi_node_deepseek_v3_1_2nodes/node1/run_serve.sh
grep -n -- "--data-parallel-size=4" ./multi_node_deepseek_v3_1_2nodes/node0/run_serve.sh
grep -n -- "--data-parallel-size-local=2" ./multi_node_deepseek_v3_1_2nodes/node0/run_serve.sh
grep -n -- "--data-parallel-start-rank=0" ./multi_node_deepseek_v3_1_2nodes/node0/run_serve.sh
grep -n -- "--data-parallel-start-rank=2" ./multi_node_deepseek_v3_1_2nodes/node1/run_serve.sh
grep -n -- "--data-parallel-address=192.168.1.10" ./multi_node_deepseek_v3_1_2nodes/node0/run_serve.sh
grep -n -- "--data-parallel-address=192.168.1.10" ./multi_node_deepseek_v3_1_2nodes/node1/run_serve.sh
grep -n "工作流执行日志" ./multi_node_deepseek_v3_1_2nodes/README.md
grep -n "启动顺序" ./multi_node_deepseek_v3_1_2nodes/README.md
if grep -q -- "--headless" ./multi_node_deepseek_v3_1_2nodes/node0/run_serve.sh; then
  echo "node0 should not be headless" && exit 1
fi
```

## 第 4 步：对比基线

```bash
diff -rq \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志` 和 `启动顺序`

## 第 5 步：更新基线

当确认输出结果正确后，可更新基线：

```bash
rm -rf ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline/*
cp -r ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/output/* \
  ./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/baseline/
```

## 边界验证

模型教程缺失 `Multi-node Deployment` 章节时，skill 必须立即停止，不能继续生成目录或脚本。