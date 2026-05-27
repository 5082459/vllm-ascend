from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    import sys
    from pathlib import Path
    # Add tests directory to path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.common import (
        build_cmd,
        dump_json,
        ensure_dir,
        run_command,
        timestamp_slug,
    )
else:
    from tests.tools.common import (
        build_cmd,
        dump_json,
        ensure_dir,
        run_command,
        timestamp_slug,
    )


@dataclass
class EvalItemResult:
    query: str
    should_trigger: bool
    actual_trigger: bool
    pass_result: bool
    confidence: float
    reason: str
    matched_terms: list[str]
    raw_output: str


def build_eval_prompt(skill_name: str, skill_description: str, query: str) -> str:
    return f"""You are evaluating whether a single Claude skill should be used for a user query.

Skill name: {skill_name}
Skill description: {skill_description}
User query: {query}

Decide only whether this specific skill should be used for the query.
Return exactly one JSON object with this schema:
{{
  "should_use_skill": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "short explanation",
  "matched_terms": ["term1", "term2"]
}}

Do not include markdown fences. Output JSON only.
"""


def _extract_json_text(raw: str) -> str:
    start = raw.find("{")
    if start == -1:
        raise ValueError("No JSON object found in output")

    depth = 0
    for index in range(start, len(raw)):
        char = raw[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw[start : index + 1]
    raise ValueError("Unterminated JSON object in output")


def _extract_agent_message_json_text(raw: str) -> str | None:
    """
    Extract agent message from Claude's stream-json output format.

    Claude stream-json format has lines like:
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "..."}]}}
    or for newer versions:
    {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "..."}}
    {"type": "result", "result": "..."}
    """
    # Priority 1: Check for result message first (contains the final output)
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        if payload.get("type") == "result":
            result_text = payload.get("result", "")
            if result_text:
                return result_text

    # Priority 2: Fallback to assistant message content
    collected_text = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        if payload.get("type") == "assistant":
            message = payload.get("message", {})
            content = message.get("content", [])
            for block in content:
                if block.get("type") == "text":
                    collected_text.append(block.get("text", ""))
        elif payload.get("type") == "content_block_delta":
            delta = payload.get("delta", {})
            if delta.get("type") == "text_delta":
                collected_text.append(delta.get("text", ""))

    if collected_text:
        return "".join(collected_text)
    return None


def parse_eval_response(raw: str) -> dict:
    agent_message_text = _extract_agent_message_json_text(raw)
    json_text = agent_message_text or _extract_json_text(raw)
    payload = json.loads(json_text)
    if "should_use_skill" not in payload:
        raise ValueError("Missing should_use_skill in eval response")
    return payload


def summarize_results(skill_name: str, description: str, results: list[EvalItemResult]) -> dict:
    output_results = []
    for item in results:
        row = asdict(item)
        row["pass"] = row.pop("pass_result")
        row["triggered"] = row.pop("actual_trigger")
        output_results.append(row)

    passed = sum(1 for item in results if item.pass_result)
    total = len(results)
    return {
        "skill_name": skill_name,
        "description": description,
        "results": output_results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def run_eval(
    skill_path: Path,
    eval_set_path: Path,
    runner_bin: str,
    timeout_sec: float,
    runs_dir: Path | None,
) -> dict:
    skill_md = skill_path / "SKILL.md"
    skill_text = skill_md.read_text(encoding="utf-8")
    lines = skill_text.splitlines()
    skill_name = ""
    description = ""
    for line in lines:
        if line.startswith("name:"):
            skill_name = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            description = line.split(":", 1)[1].strip().strip('"').strip("'")
        if skill_name and description:
            break

    if not skill_name or not description:
        raise ValueError(f"Could not parse name/description from {skill_md}")

    eval_set = json.loads(eval_set_path.read_text(encoding="utf-8"))
    results: list[EvalItemResult] = []
    run_dir = None
    if runs_dir is not None:
        run_dir = runs_dir / timestamp_slug()
        ensure_dir(run_dir)

    workspace_root = skill_path.parent.parent
    for idx, item in enumerate(eval_set, start=1):
        prompt = build_eval_prompt(skill_name, description, item["query"])
        cmd = build_cmd(
            runner_bin=runner_bin,
            prompt=prompt,
            cwd=workspace_root,
            output_format="stream-json",
        )
        command_result = run_command(cmd, cwd=workspace_root, stdin_text=None, timeout_sec=timeout_sec)
        raw_output = command_result.stdout or command_result.stderr
        try:
            parsed = parse_eval_response(raw_output)
            actual = bool(parsed["should_use_skill"])
            confidence = float(parsed.get("confidence", 0.0))
            reason = str(parsed.get("reason", ""))
            matched_terms = list(parsed.get("matched_terms", []))
        except Exception as exc:  # noqa: BLE001
            actual = False
            confidence = 0.0
            reason = f"Failed to parse eval response: {exc}"
            matched_terms = []

        result = EvalItemResult(
            query=item["query"],
            should_trigger=bool(item["should_trigger"]),
            actual_trigger=actual,
            pass_result=(actual == bool(item["should_trigger"])),
            confidence=confidence,
            reason=reason,
            matched_terms=matched_terms,
            raw_output=raw_output,
        )
        results.append(result)

        if run_dir is not None:
            dump_json(
                run_dir / f"{idx:02d}.json",
                {
                    "query": item["query"],
                    "should_trigger": item["should_trigger"],
                    "command_result": command_result.to_dict(),
                    "parsed": {
                        "actual_trigger": actual,
                        "confidence": confidence,
                        "reason": reason,
                        "matched_terms": matched_terms,
                    },
                },
            )

    return summarize_results(skill_name, description, results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Claude-native trigger evaluation for a skill")
    parser.add_argument("--skill-path", required=True)
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--timeout-sec", type=float, default=120.0)
    parser.add_argument("--runs-dir", default=None)
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args()

    payload = run_eval(
        skill_path=Path(args.skill_path),
        eval_set_path=Path(args.eval_set),
        runner_bin=args.claude_bin,
        timeout_sec=args.timeout_sec,
        runs_dir=Path(args.runs_dir) if args.runs_dir else None,
    )
    if args.output_json:
        dump_json(Path(args.output_json), payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()