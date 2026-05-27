from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CommandResult:
    args: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_sec: float

    def to_dict(self) -> dict:
        return asdict(self)


def build_cmd(
    runner_bin: str,
    prompt: str,
    cwd: Path,
    output_format: str = "stream-json",
    extra_args: list[str] | None = None,
) -> list[str]:
    """
    Build Skills CLI command.

    Uses `runner -p "prompt"` with `--output-format stream-json`.
    Uses cwd directly for directory context.
    """
    cmd = [runner_bin, "-p", prompt]
    cmd.extend(["--output-format", output_format])
    cmd.append("--verbose")
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def run_command(
    args: list[str],
    cwd: Path,
    stdin_text: str | None,
    timeout_sec: float,
) -> CommandResult:
    """Run command with UTF-8 encoding forced on Windows."""
    def normalize_output(value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    start = time.monotonic()
    # Force UTF-8 encoding on Windows
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"

    try:
        # Use binary mode and decode manually to avoid Windows encoding issues
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            input=stdin_text.encode("utf-8") if stdin_text else None,
            capture_output=True,  # binary mode
            timeout=timeout_sec,
            env=env,
        )
        return CommandResult(
            args=args,
            cwd=str(cwd),
            returncode=completed.returncode,
            stdout=completed.stdout.decode("utf-8", errors="replace"),
            stderr=completed.stderr.decode("utf-8", errors="replace"),
            timed_out=False,
            duration_sec=time.monotonic() - start,
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            args=args,
            cwd=str(cwd),
            returncode=-1,
            stdout=normalize_output(exc.stdout),
            stderr=normalize_output(exc.stderr),
            timed_out=True,
            duration_sec=time.monotonic() - start,
        )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def timestamp_slug() -> str:
    return time.strftime("%Y%m%d-%H%M%S")