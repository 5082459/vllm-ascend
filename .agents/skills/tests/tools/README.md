# Claude 测试工具

## 文件说明

- `common.py`：Skills CLI 调用与公共工具
- `exec_eval.py`：Claude 原生触发测试
- `exec_behavior.py`：Claude 原生行为测试
- `baseline_compare.py`：基线创建与对比

## 设计原则

- 统一通过 `runner -p` 执行非交互测试
- 所有运行记录可落到 `tests/<skill>/runs/`
- 触发测试汇总可通过 `--output-json` 固定落盘
- 基线比较默认严格检查脚本与配置，只对 README 做关键段落检查

## Skills CLI 命令格式

```bash
runner -p "prompt text" \
  --output-format stream-json \
  --verbose
```