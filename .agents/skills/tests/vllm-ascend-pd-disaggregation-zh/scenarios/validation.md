# vllm-ascend-pd-disaggregation-zh 验证流程

## 目标

验证 PD 分离 skill 的三层正确性：

1. `SKILL.md` 结构合法。
2. PD 分离请求能触发，其他请求不会误触发。
3. 生成的目录、脚本和 README 符合 PD 分离预期。

## 基线约定

- 触发基线：`./tests/vllm-ascend-pd-disaggregation-zh/trigger/eval-summary.json`
- 行为基线：
  - DeepSeek-V4-Pro (1P1N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/baseline/`
  - DeepSeek-V4-Pro (1P2N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/baseline/`
  - DeepSeek-V4-Pro (2P2N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/baseline/`
  - GLM5：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_glm5_1p1n_1d1n/baseline/`
- 输出目录：
  - DeepSeek-V4-Pro (1P1N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output/`
  - DeepSeek-V4-Pro (1P2N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output/`
  - DeepSeek-V4-Pro (2P2N+1D2N)：`./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/output/`
- 运行记录：`./tests/vllm-ascend-pd-disaggregation-zh/runs/`

## 第 1 步：结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-pd-disaggregation-zh
```

通过标准：

```text
Skill is valid!
```

## 第 2 步：触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./vllm-ascend-pd-disaggregation-zh \
  --eval-set ./tests/vllm-ascend-pd-disaggregation-zh/trigger/eval.json \
  --runs-dir ./tests/vllm-ascend-pd-disaggregation-zh/runs/trigger \
  --output-json ./tests/vllm-ascend-pd-disaggregation-zh/runs/trigger/latest.json
```

通过标准：

- PD 分离正例全部触发
- 单节点、多节点和无关请求全部不触发

对比基线：

```bash
diff -u \
  ./tests/vllm-ascend-pd-disaggregation-zh/trigger/eval-summary.json \
  ./tests/vllm-ascend-pd-disaggregation-zh/runs/trigger/latest.json
```

## 第 3 步：行为测试

**场景：DeepSeek-V4-Pro (1p1n_1d2n)**

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/deepseek-v4-pro.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-pd-disaggregation-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 600
```

输出产物目录：`./pd_disaggregation_deepseek_v4_pro_1p1n_1d2n/`

关键检查点：

- 存在 `prefill/`、`decode/`、`proxy/`、`sources/`
- prefill 包含 `instance1/node1`
- decode 包含 `instance1/node1`、`instance1/node2`
- prefill 中包含 `kv_role: kv_producer`
- decode 中包含 `kv_role: kv_consumer`
- `engine_id` 分别为 `1` 和 `2`
- `kv_port` 分别为 `36000` 和 `36200`
- `README.md` 包含 `工作流执行日志`

拷贝输出到场景 output 目录：

```bash
cp -r ./pd_disaggregation_deepseek_v4_pro_1p1n_1d2n/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output/
```

**场景：DeepSeek-V4-Pro (1p2n_1d2n)**

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/deepseek-v4-pro.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-pd-disaggregation-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 600
```

输出产物目录：`./pd_disaggregation_deepseek_v4_pro_1p2n_1d2n/`

关键检查点：

- 存在 `prefill/`、`decode/`、`proxy/`、`sources/`
- prefill 包含 `instance1/node1`、`instance1/node2`
- decode 包含 `instance1/node1`、`instance1/node2`
- prefill 中包含 `kv_role: kv_producer`
- decode 中包含 `kv_role: kv_consumer`
- `engine_id` 分别为 `1` 和 `2`
- `kv_port` 分别为 `36000` 和 `36200`
- `README.md` 包含 `工作流执行日志`

拷贝输出到场景 output 目录：

```bash
cp -r ./pd_disaggregation_deepseek_v4_pro_1p2n_1d2n/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output/
```

**场景：DeepSeek-V4-Pro (2p2n_1d2n)**

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/deepseek-v4-pro.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-pd-disaggregation-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 600
```

输出产物目录：`./pd_disaggregation_deepseek_v4_pro_2p2n_1d2n/`

关键检查点：

- 存在 `prefill/`、`decode/`、`proxy/`、`sources/`
- prefill 包含 `instance1/node1`、`instance1/node2` 和 `instance2/node1`、`instance2/node2`
- decode 包含 `instance1/node1`、`instance1/node2`
- prefill 中包含 `kv_role: kv_producer`
- decode 中包含 `kv_role: kv_consumer`
- `engine_id`：instance1 为 `1`，instance2 为 `3`
- `kv_port` 分别为 `36000` 和 `36200`
- `README.md` 包含 `工作流执行日志`

拷贝输出到场景 output 目录：

```bash
cp -r ./pd_disaggregation_deepseek_v4_pro_2p2n_1d2n/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/output/
```

**场景：GLM5 (1p1n_1d1n)**

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_glm5_1p1n_1d1n/glm5.md \
  --workspace-root . \
  --runs-dir ./tests/vllm-ascend-pd-disaggregation-zh/runs/behavior \
  --runner-bin claude \
  --timeout-sec 600
```

输出产物目录：`./pd_disaggregation_glm5_1p1n_1d1n/`

关键检查点：

- 存在 `prefill/`、`decode/`、`proxy/`、`sources/`
- prefill 包含 `instance1/node1`
- decode 包含 `instance1/node1`
- prefill 中包含 `kv_role: kv_producer`
- decode 中包含 `kv_role: kv_consumer`
- `engine_id` 分别为 `1` 和 `2`
- `kv_port` 分别为 `36000` 和 `36100`

## 第 4 步：对比基线

**DeepSeek-V4-Pro (1P1N+1D2N) 场景**：

```bash
diff -rq \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/baseline \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

**DeepSeek-V4-Pro (1P2N+1D2N) 场景**：

```bash
diff -rq \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/baseline \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

## 第 5 步：更新基线

当确认输出结果正确后，可更新基线：

```bash
# DeepSeek-V4-Pro (1P1N+1D2N) 场景
rm -rf ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/baseline/*
cp -r ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/baseline/

# DeepSeek-V4-Pro (1P2N+1D2N) 场景
rm -rf ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/baseline/*
cp -r ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/baseline/

# DeepSeek-V4-Pro (2P2N+1D2N) 场景
rm -rf ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/baseline/*
cp -r ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/output/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/baseline/
```

## 边界验证

模型教程缺失 `Prefill-Decode Disaggregation` 章节时，skill 必须立即停止，不能继续生成 `prefill/`、`decode/` 或 `proxy/`。