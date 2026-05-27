from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.common import (
        dump_json,
        ensure_dir,
        run_command,
        timestamp_slug,
    )
else:
    from tests.tools.common import (
        dump_json,
        ensure_dir,
        run_command,
        timestamp_slug,
    )


def build_behavior_prompt(scenario_text: str) -> str:
    return f"""You are running an automated behavior validation scenario.

Follow these rules exactly:
- Treat the scenario below as authoritative test input.
- Treat every value in the scenario's parameter table as already provided by the user.
- Map those parameter values directly to the skill's expected inputs and execute with them.
- Do not ask the user clarifying questions.
- Do not use brainstorming, writing-plans, or other meta-planning skills.
- This is not a design exercise. It is an execution-only validation run.
- Prefer directly invoking the most specific deployment skill implied by the scenario.
- If the scenario includes parameter tables or expected output names, use them directly.
- Complete the applicable skill workflow end-to-end in the current workspace.
- If you find a mismatch between scenario wording and upstream source content, continue with the actual source content and mention the discrepancy in your final response instead of asking a question.

Scenario:

{scenario_text}
"""


def run_behavior(
    prompt_file: Path,
    workspace_root: Path,
    runner_bin: str,
    timeout_sec: float,
    runs_dir: Path,
) -> Path:
    ensure_dir(runs_dir)
    run_dir = runs_dir / timestamp_slug()
    ensure_dir(run_dir)

    scenario_text = prompt_file.read_text(encoding="utf-8")
    prompt_text = build_behavior_prompt(scenario_text)

    # CLI uses stdin with `-p -` to read prompt from stdin
    cmd = [runner_bin, "-p", "-", "--output-format", "stream-json", "--verbose"]

    result = run_command(cmd, cwd=workspace_root, stdin_text=prompt_text, timeout_sec=timeout_sec)

    (run_dir / "scenario.md").write_text(scenario_text, encoding="utf-8")
    (run_dir / "prompt.md").write_text(prompt_text, encoding="utf-8")
    (run_dir / "stdout.txt").write_text(result.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    dump_json(run_dir / "result.json", result.to_dict())
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a behavior scenario through CLI")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--runner-bin", default="runner")
    parser.add_argument("--timeout-sec", type=float, default=300.0)
    parser.add_argument("--runs-dir", required=True)
    args = parser.parse_args()

    run_dir = run_behavior(
        prompt_file=Path(args.prompt_file),
        workspace_root=Path(args.workspace_root),
        runner_bin=args.runner_bin,
        timeout_sec=args.timeout_sec,
        runs_dir=Path(args.runs_dir),
    )
    print(run_dir)


if __name__ == "__main__":
    main()