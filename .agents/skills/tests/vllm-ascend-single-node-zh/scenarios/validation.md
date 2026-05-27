# vllm-ascend-single-node-zh 验证流程

## 目标

验证单节点 skill 的三层正确性：

1. `SKILL.md` 结构合法。
2. 单节点请求能触发，其他请求不会误触发。
3. 生成的目录、脚本和 README 符合单节点预期。

## 基线约定

- 触发基线：`./tests/vllm-ascend-single-node-zh/trigger/eval-summary.json`
- 行为基线：`./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/baseline/`
- 输出目录：`./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/output/`
- 运行记录：`./tests/vllm-ascend-single-node-zh/runs/`

## 第 1 步：结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-single-node-zh
```

通过标准：

```text
Skill is valid!
```

## 第 2 步：触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./vllm-ascend-single-node-zh \
  --eval-set ./tests/vllm-ascend-single-node-zh/trigger/eval.json \
  --runs-dir ./tests/vllm-ascend-single-node-zh/runs/trigger \
  --output-json ./tests/vllm-ascend-single-node-zh/runs/trigger/latest.json
```

通过标准：

- 单节点正例全部触发
- 多节点、PD 分离和无关请求全部不触发

对比基线：

```bash
diff -u \
  ./tests/vllm-ascend-single-node-zh/trigger/eval-summary.json \
  ./tests/vllm-ascend-single-node-zh/runs/trigger/latest.json
```

## 第 3 步：行为测试

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-single-node-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 300
```

输出产物目录：`./single_node_deepseek_v3_1/`

拷贝输出到场景 output 目录：

```bash
cp -r ./single_node_deepseek_v3_1/* \
  ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/output/
```

关键检查点：

- 存在 `sources/` 和 `node/`
- `node/run_serve.sh` 包含 `--data-parallel-size=4`
- `node/run_serve.sh` 包含 `--tensor-parallel-size=4`
- `node/run_serve.sh` 不包含 `--data-parallel-address`
- `node/run_serve.sh` 保留 `192.168.1.100`
- `README.md` 包含 `工作流执行日志`

建议检查命令：

```bash
find ./single_node_deepseek_v3_1 -maxdepth 2 -type f | sort
grep -n -- "--data-parallel-size=4" ./single_node_deepseek_v3_1/node/run_serve.sh
grep -n -- "--tensor-parallel-size=4" ./single_node_deepseek_v3_1/node/run_serve.sh
grep -n -- "192.168.1.100" ./single_node_deepseek_v3_1/node/run_serve.sh
grep -n "工作流执行日志" ./single_node_deepseek_v3_1/README.md
if grep -q -- "--data-parallel-address" ./single_node_deepseek_v3_1/node/run_serve.sh; then
  echo "unexpected multi-node arg found" && exit 1
fi
```

## 第 4 步：对比基线

```bash
diff -rq \
  ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/baseline \
  ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

## 第 5 步：更新基线

当确认输出结果正确后，可更新基线：

```bash
rm -rf ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/baseline/*
cp -r ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/output/* \
  ./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/baseline/
```

## 边界验证

模型教程缺失 `Single-node Deployment` 章节时，skill 必须立即停止，不能继续生成目录或脚本。