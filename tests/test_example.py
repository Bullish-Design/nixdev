from __future__ import annotations

import difflib
import filecmp
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _collect_dir_differences(
    expected: Path, actual: Path, relative: Path = Path("")
) -> list[str]:
    comparison = filecmp.dircmp(expected, actual)
    issues: list[str] = []

    for name in sorted(comparison.left_only):
        issues.append(f"Only in expected: {relative / name}")
    for name in sorted(comparison.right_only):
        issues.append(f"Only in output: {relative / name}")

    for name in sorted(comparison.diff_files):
        expected_file = expected / name
        actual_file = actual / name
        issues.append(f"File differs: {relative / name}")
        issues.extend(_diff_file(expected_file, actual_file, relative / name))

    for subdir in sorted(comparison.common_dirs):
        issues.extend(
            _collect_dir_differences(
                expected / subdir,
                actual / subdir,
                relative / subdir,
            )
        )

    return issues


def _diff_file(expected: Path, actual: Path, relative: Path) -> list[str]:
    try:
        expected_lines = expected.read_text(encoding="utf-8").splitlines()
        actual_lines = actual.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [f"Binary or non-UTF8 file differs: {relative}"]

    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile=str(expected),
        tofile=str(actual),
        lineterm="",
    )
    return [f"  {line}" for line in diff]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    templates_dir = repo_root / "tests" / "templates"
    expected_dir = templates_dir / "expected" / "python"
    output_root = templates_dir / "output"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = output_root / f"python_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["NIXDEV_TEMPLATE_PYTHON"] = str(templates_dir / "python")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "nixdev.cli",
            "create",
            "python",
            str(output_dir),
            "--no-interactive",
            "--project-name",
            "Example Project",
            "--python-version",
            "3.12",
        ],
        check=True,
        env=env,
    )

    differences = _collect_dir_differences(expected_dir, output_dir)
    if differences:
        message = "\n".join(differences)
        print("Template output differs from expected:\n", message, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
