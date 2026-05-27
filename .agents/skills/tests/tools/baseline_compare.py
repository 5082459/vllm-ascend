from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.common import dump_json, ensure_dir
else:
    from tests.tools.common import dump_json, ensure_dir


README_SECTION_HINTS = ["工作流执行日志", "启动顺序"]


@dataclass
class ArtifactDiff:
    non_readme_match: bool
    missing_readme_sections: list[str]
    mismatched_files: list[str]
    missing_files: list[str]
    extra_files: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def extract_required_readme_sections(text: str) -> list[str]:
    sections: list[str] = []
    for hint in README_SECTION_HINTS:
        if hint in text and hint not in sections:
            sections.append(hint)
    return sections


def _list_relative_files(root: Path) -> set[str]:
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
    }


def compare_artifacts(
    baseline_dir: Path,
    artifact_dir: Path,
    required_readme_sections: list[str],
) -> ArtifactDiff:
    baseline_files = _list_relative_files(baseline_dir)
    artifact_files = _list_relative_files(artifact_dir)

    missing_files = sorted(file for file in baseline_files - artifact_files if file != "README.md")
    extra_files = sorted(file for file in artifact_files - baseline_files if file != "README.md")
    shared_files = sorted((baseline_files & artifact_files) - {"README.md"})

    mismatched_files: list[str] = []
    for rel_path in shared_files:
        if not filecmp.cmp(baseline_dir / rel_path, artifact_dir / rel_path, shallow=False):
            mismatched_files.append(rel_path)

    readme_text = (artifact_dir / "README.md").read_text(encoding="utf-8") if (artifact_dir / "README.md").exists() else ""
    missing_sections = [section for section in required_readme_sections if section not in readme_text]

    return ArtifactDiff(
        non_readme_match=not (missing_files or extra_files or mismatched_files),
        missing_readme_sections=missing_sections,
        mismatched_files=mismatched_files,
        missing_files=missing_files,
        extra_files=extra_files,
    )


def infer_behavior_scenario(skill_dir: Path) -> str:
    name = skill_dir.name
    if "single-node" in name:
        return "single-node"
    if "multi-node" in name:
        return "multi-node"
    if "pd-disaggregation" in name:
        return "pd-disaggregation"
    raise ValueError(f"Cannot infer behavior scenario from {name}")


def create_baseline(skill_dir: Path, artifact_dir: Path, scenario: str | None = None) -> Path:
    chosen_scenario = scenario or infer_behavior_scenario(skill_dir)
    target = skill_dir / "baseline" / "behavior" / chosen_scenario
    if target.exists():
        shutil.rmtree(target)
    ensure_dir(target)
    for item in artifact_dir.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    return target


def compare_with_skill_baseline(skill_dir: Path, artifact_dir: Path, scenario: str | None = None) -> ArtifactDiff:
    chosen_scenario = scenario or infer_behavior_scenario(skill_dir)
    baseline_dir = skill_dir / "baseline" / "behavior" / chosen_scenario
    validation_text = (skill_dir / "validation.md").read_text(encoding="utf-8")
    required_sections = extract_required_readme_sections(validation_text)
    return compare_artifacts(
        baseline_dir=baseline_dir,
        artifact_dir=artifact_dir,
        required_readme_sections=required_sections,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or compare skill behavior baselines")
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--create-baseline", action="store_true")
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    artifact_dir = Path(args.artifact_dir)

    if args.create_baseline:
        baseline_dir = create_baseline(skill_dir, artifact_dir, args.scenario)
        payload = {"baseline_dir": str(baseline_dir)}
    else:
        diff = compare_with_skill_baseline(skill_dir, artifact_dir, args.scenario)
        payload = diff.to_dict()

    if args.output_json:
        dump_json(Path(args.output_json), payload)
    print(payload)


if __name__ == "__main__":
    main()