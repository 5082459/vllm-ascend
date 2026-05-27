# vllm-ascend-inference-generator-zh 验证流程

## 目标

验证主技能是否满足三件事：

1. `SKILL.md` 结构合法。
2. 主技能能被正确触发，不会误触发到无关请求。
3. 主技能能把请求正确分流到三个子技能场景。

主技能本身不直接产出部署目录，所以它的基线重点是 trigger 结果；行为正确性通过三个子技能场景覆盖。

## 基线约定

- 触发基线：`./tests/vllm-ascend-inference-generator-zh/trigger/eval-summary.json`
- 运行记录：`./tests/vllm-ascend-inference-generator-zh/runs/`

## 第 1 步：结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-inference-generator-zh
```

通过标准：

```text
Skill is valid!
```

## 第 2 步：触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./vllm-ascend-inference-generator-zh \
  --eval-set ./tests/vllm-ascend-inference-generator-zh/trigger/eval.json \
  --runs-dir ./tests/vllm-ascend-inference-generator-zh/runs/trigger \
  --output-json ./tests/vllm-ascend-inference-generator-zh/runs/trigger/latest.json
```

通过标准：

- `should_trigger: true` 的请求全部命中
- `should_trigger: false` 的请求全部不命中

对比基线：

```bash
diff -u \
  ./tests/vllm-ascend-inference-generator-zh/trigger/eval-summary.json \
  ./tests/vllm-ascend-inference-generator-zh/runs/trigger/latest.json
```

## 第 3 步：行为分流验证

主技能行为验证不单独使用自己的 `behavior.md`，而是直接复用三个子技能的标准场景：

- `./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md`
- `./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md`
- `./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/deepseek-v4-pro.md`

推荐顺序：

1. 单节点场景
2. 多节点场景
3. PD 分离场景

每个场景都应确认：

- 主技能先识别部署模式
- 主技能选择了正确的子技能
- 子技能完成产物生成
- 产物 README 包含 `工作流执行日志`
- 对于不支持的模型或模式，流程会立即停止

## 快速闭环

如果只做一轮最小验证，按下面顺序执行：

1. 运行 `quick_validate.py`
2. 运行 `exec_eval.py`
3. 至少跑一个子技能行为场景

如果要作为发布前验证，三个子技能场景都应执行。