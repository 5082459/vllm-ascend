# vllm-ascend-pd-disaggregation-zh 测试入口

## 目录结构

```
tests/vllm-ascend-pd-disaggregation-zh/
├── README.md                                    # 本文件
├── trigger/                                     # 触发测试
│   ├── eval.json                                # 触发测试用例定义
│   └── eval-summary.json                        # 触发测试基线结果
├── scenarios/                                   # 测试场景
│   ├── validation.md                            # 验证标准
│   ├── pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/
│   │   ├── deepseek-v4-pro.md                   # 测试输入场景
│   │   └── baseline/                            # DeepSeek-V4-Pro (1P1N+1D2N) 基线
│   │       ├── prefill/                         # Prefill 节点脚本基线
│   │       ├── decode/                          # Decode 节点脚本基线
│   │       ├── proxy/                           # Proxy 脚本基线
│   │       └── sources/                         # 原始模板基线
│   ├── pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/
│   │   ├── deepseek-v4-pro.md                   # 测试输入场景
│   │   ├── baseline/                            # DeepSeek-V4-Pro (1P2N+1D2N) 基线
│   │   │   ├── prefill/                         # Prefill 节点脚本基线
│   │   │   ├── decode/                          # Decode 节点脚本基线
│   │   │   ├── proxy/                           # Proxy 脚本基线
│   │   │   └── sources/                         # 原始模板基线
│   ├── pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/
│   │   ├── deepseek-v4-pro.md                   # 测试输入场景
│   │   ├── baseline/                            # DeepSeek-V4-Pro (2P2N+1D2N) 基线
│   │   │   ├── prefill/                         # Prefill 节点脚本基线
│   │   │   ├── decode/                          # Decode 节点脚本基线
│   │   │   ├── proxy/                           # Proxy 脚本基线
│   │   │   └── sources/                         # 原始模板基线
│   └── pd_disaggregation_glm5_1p1n_1d1n/
│       ├── glm5.md                              # 测试输入场景
│       └── baseline/                            # GLM5 基线
│           ├── prefill/                         # Prefill 节点脚本基线
│           ├── decode/                          # Decode 节点脚本基线
│           ├── proxy/                           # Proxy 脚本基线
│           └── sources/                         # 原始模板基线
└── runs/                                        # 测试运行记录
    ├── trigger/                                 # 触发测试记录
    └── behavior/                                # 行为测试记录（按时间戳）
```

## 测试执行

### 1. 结构合法性

```bash
python "C:/Users/Administrator/.claude/skills/skill-creator/scripts/quick_validate.py" \
  ./vllm-ascend-pd-disaggregation-zh
```

通过标准：

```text
Skill is valid!
```

### 2. 触发测试

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

### 3. 行为测试

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

拷贝输出到场景 output 目录：

```bash
cp -r ./pd_disaggregation_glm5_1p1n_1d1n/* \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_glm5_1p1n_1d1n/output/
```

### 4. 对比基线

**DeepSeek-V4-Pro (1P1N+1D2N) 场景对比**：

```bash
diff -rq \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/baseline \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

**DeepSeek-V4-Pro (1P2N+1D2N) 场景对比**：

```bash
diff -rq \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/baseline \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

**DeepSeek-V4-Pro (2P2N+1D2N) 场景对比**：

```bash
diff -rq \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/baseline \
  ./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/output
```

通过标准：

- 非 `README.md` 文件全部严格一致
- `README.md` 至少包含 `工作流执行日志`

### 5. 更新基线

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

### 6. 关键验证点

**DeepSeek-V4-Pro (1p1n_1d2n)**：

```bash
OUTPUT_DIR="./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p1n_1d2n/output"

# 目录结构
find $OUTPUT_DIR -maxdepth 4 -type d | sort

# Prefill 配置
grep -R "kv_producer" $OUTPUT_DIR/prefill
grep -R "engine_id.*1" $OUTPUT_DIR/prefill
grep -R "kv_port.*36000" $OUTPUT_DIR/prefill

# Decode 配置
grep -R "kv_consumer" $OUTPUT_DIR/decode
grep -R "engine_id.*2" $OUTPUT_DIR/decode
grep -R "kv_port.*36200" $OUTPUT_DIR/decode

# README 检查
grep -n "工作流执行日志" $OUTPUT_DIR/README.md
```

**DeepSeek-V4-Pro (1p2n_1d2n)**：

```bash
OUTPUT_DIR="./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_1p2n_1d2n/output"

# 目录结构
find $OUTPUT_DIR -maxdepth 4 -type d | sort

# Prefill 配置
grep -R "kv_producer" $OUTPUT_DIR/prefill
grep -R "engine_id.*1" $OUTPUT_DIR/prefill
grep -R "kv_port.*36000" $OUTPUT_DIR/prefill

# Decode 配置
grep -R "kv_consumer" $OUTPUT_DIR/decode
grep -R "engine_id.*2" $OUTPUT_DIR/decode
grep -R "kv_port.*36200" $OUTPUT_DIR/decode

# README 检查
grep -n "工作流执行日志" $OUTPUT_DIR/README.md
```

**DeepSeek-V4-Pro (2p2n_1d2n)**：

```bash
OUTPUT_DIR="./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_deepseek-v4-pro_2p2n_1d2n/output"

# 目录结构
find $OUTPUT_DIR -maxdepth 4 -type d | sort

# Prefill 配置 (2 instances)
grep -R "kv_producer" $OUTPUT_DIR/prefill
grep -R "engine_id.*1" $OUTPUT_DIR/prefill/instance1
grep -R "engine_id.*3" $OUTPUT_DIR/prefill/instance2
grep -R "kv_port.*36000" $OUTPUT_DIR/prefill

# Decode 配置
grep -R "kv_consumer" $OUTPUT_DIR/decode
grep -R "engine_id.*2" $OUTPUT_DIR/decode
grep -R "kv_port.*36200" $OUTPUT_DIR/decode

# README 检查
grep -n "工作流执行日志" $OUTPUT_DIR/README.md
```

**GLM5 (1p1n_1d1n)**：

```bash
OUTPUT_DIR="./tests/vllm-ascend-pd-disaggregation-zh/scenarios/pd_disaggregation_glm5_1p1n_1d1n/output"

# 目录结构
find $OUTPUT_DIR -maxdepth 4 -type d | sort

# Prefill 配置
grep -R "kv_producer" $OUTPUT_DIR/prefill
grep -R "engine_id.*1" $OUTPUT_DIR/prefill

# Decode 配置
grep -R "kv_consumer" $OUTPUT_DIR/decode
grep -R "engine_id.*2" $OUTPUT_DIR/decode

# README 检查
grep -n "工作流执行日志" $OUTPUT_DIR/README.md
```