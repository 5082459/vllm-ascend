# Skills 测试入口

## 当前标准流程

本仓库的 skill 测试统一采用 **Skills 原生流程**。

统一入口：

- 触发测试：`tests/tools/exec_eval.py`
- 行为测试：`tests/tools/exec_behavior.py`

## 目录约定

```text
tests/
├── README.md
├── tools/
│   ├── common.py
│   ├── exec_eval.py
│   └── behavior.py
├── vllm-ascend-inference-generator-zh/
├── vllm-ascend-single-node-zh/
├── vllm-ascend-multi-node-zh/
├── vllm-ascend-pd-disaggregation-zh/
└── case-study-writer-zh/
```

每个 skill 目录内统一包含：

```
tests/{skill-name}/
├── README.md                                    # 测试入口
├── trigger/                                     # 触发测试
│   ├── eval.json                                # 触发测试用例定义
│   └── eval-summary.json                        # 触发测试基线结果
├── scenarios/                                   # 测试场景
│   ├── validation.md                            # 验证标准
│   └── {scenario-name}/
│       ├── {scenario-name}.md                   # 测试输入场景
│       ├── baseline/                            # 场景基线
│       ├── materials/                           # 测试输入材料（如有）
│       └── output/                              # 运行结果输出目录
└── runs/                                        # 测试运行记录
    ├── trigger/                                 # 触发测试记录
    └── behavior/                                # 行为测试记录（按时间戳）
```

## 通用命令

### 1. 结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./<skill-dir>
```

### 2. 触发测试

```bash
python tests/tools/exec_eval.py \
  --skill-path ./<skill-dir> \
  --eval-set ./tests/<skill-name>/trigger/eval.json \
  --runs-dir ./tests/<skill-name>/runs/trigger \
  --output-json ./tests/<skill-name>/runs/trigger/latest.json
```

对比基线：

```bash
diff -u \
  ./tests/<skill-name>/trigger/eval-summary.json \
  ./tests/<skill-name>/runs/trigger/latest.json
```

### 3. 行为测试

```bash
python tests/tools/exec_behavior.py \
  --prompt-file ./tests/<skill-name>/scenarios/<scenario-name>/<scenario-name>.md \
  --workspace-root ./tests/<skill-name>/scenarios/<scenario-name>/output \
  --runs-dir ./tests/<skill-name>/runs/behavior
```

### 4. 对比基线

```bash
diff -rq \
  ./tests/<skill-name>/scenarios/<scenario-name>/baseline \
  ./tests/<skill-name>/scenarios/<scenario-name>/output
```

### 5. 更新基线

当确认输出结果正确后，可更新基线：

```bash
rm -rf ./tests/<skill-name>/scenarios/<scenario-name>/baseline/*
cp -r ./tests/<skill-name>/scenarios/<scenario-name>/output/* \
  ./tests/<skill-name>/scenarios/<scenario-name>/baseline/
```

## 比较规则

- 触发结果：严格对比 `trigger/eval-summary.json`
- 脚本和配置文件：严格逐文件对比
- `README.md`：只检查关键段落（工作流执行日志、启动顺序），不做全文严格对比

## Skill 测试入口

- [vllm-ascend-inference-generator-zh](vllm-ascend-inference-generator-zh/README.md) - 主技能
- [vllm-ascend-single-node-zh](vllm-ascend-single-node-zh/README.md) - 单节点部署
- [vllm-ascend-multi-node-zh](vllm-ascend-multi-node-zh/README.md) - 多节点部署
- [vllm-ascend-pd-disaggregation-zh](vllm-ascend-pd-disaggregation-zh/README.md) - PD分离部署
- [case-study-writer-zh](case-study-writer-zh/README.md) - 案例写作