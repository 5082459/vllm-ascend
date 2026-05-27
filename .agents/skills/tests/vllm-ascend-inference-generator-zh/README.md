# vllm-ascend-inference-generator-zh 测试入口

## 目录结构

```
tests/vllm-ascend-inference-generator-zh/
├── README.md                                    # 本文件
├── trigger/                                     # 触发测试
│   ├── eval.json                                # 触发测试用例定义
│   └── eval-summary.json                        # 触发测试基线结果
├── scenarios/                                   # 测试场景
│   └── validation.md                            # 验证标准
└── runs/                                        # 测试运行记录
    ├── trigger/                                 # 触发测试记录
    └── behavior/                                # 行为测试记录（按时间戳）
```

主技能不单独持有 `behavior` 场景，行为正确性通过三个子技能场景覆盖。

## 测试执行

### 1. 结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-inference-generator-zh
```

通过标准：

```text
Skill is valid!
```

### 2. 触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./vllm-ascend-inference-generator-zh \
  --eval-set ./tests/vllm-ascend-inference-generator-zh/trigger/eval.json \
  --runs-dir ./tests/vllm-ascend-inference-generator-zh/runs/trigger \
  --output-json ./tests/vllm-ascend-inference-generator-zh/runs/trigger/latest.json
```

通过标准：

- 推理部署请求全部触发
- 无关请求全部不触发

对比基线：

```bash
diff -u \
  ./tests/vllm-ascend-inference-generator-zh/trigger/eval-summary.json \
  ./tests/vllm-ascend-inference-generator-zh/runs/trigger/latest.json
```

### 3. 参考行为场景

主技能的行为测试通过子技能场景覆盖：

- `./tests/vllm-ascend-single-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md`
- `./tests/vllm-ascend-multi-node-zh/scenarios/deepseek-v3-1/deepseek-v3-1.md`
- `./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/deepseek-v4-pro.md`
- `./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_glm5_1p1n_1d1n/glm5.md`