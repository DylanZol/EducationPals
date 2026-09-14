"""Replay every documented learner command and verify its captured stdout offline."""

from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = (
    (
        "lesson-01",
        (
            ("build/lesson_01_labeled-fixtures/baseline.py", "--inspect-starter"),
            ("build/lesson_01_labeled-fixtures/baseline.py", "--validate-starter"),
            ("build/lesson_01_labeled-fixtures/baseline.py", "--write-cases"),
            ("build/lesson_01_labeled-fixtures/baseline.py",),
        ),
    ),
    (
        "lesson-02",
        (
            ("build/lesson_02_judge-contract/judge.py", "--inspect-source"),
            ("build/lesson_02_judge-contract/judge.py", "--validate-cache"),
            ("build/lesson_02_judge-contract/judge.py", "--write-judgments"),
            ("build/lesson_02_judge-contract/judge.py", "--validate-output"),
        ),
    ),
    (
        "lesson-03",
        (
            ("build/lesson_03_calibrate-grader/grader.py", "--inspect-inputs"),
            ("build/lesson_03_calibrate-grader/grader.py", "--matrix"),
            ("build/lesson_03_calibrate-grader/grader.py", "--metrics"),
            ("build/lesson_03_calibrate-grader/grader.py",),
        ),
    ),
)


def assert_output_matches(actual: str, expected: str, fixture: Path) -> None:
    """Raise a readable error when a captured run differs from its fixture."""
    if actual == expected:
        return
    diff = "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=f"{fixture} (expected)",
            tofile=f"{fixture.with_name(fixture.stem.replace('-expected', '-run') + fixture.suffix)} (actual)",
        )
    )
    raise RuntimeError(f"Output did not match {fixture.relative_to(ROOT)}:\n{diff}")


def run_lesson(commands: tuple[tuple[str, ...], ...]) -> str:
    captured: list[str] = []
    for command in commands:
        completed = subprocess.run(
            [sys.executable, *command],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            rendered_command = " ".join(("python", *command))
            raise RuntimeError(
                f"Learner command failed ({rendered_command}):\n"
                f"{completed.stdout}{completed.stderr}"
            )
        captured.append(completed.stdout)
    return "".join(captured)


def main() -> None:
    for lesson, commands in LESSONS:
        actual = run_lesson(commands)
        output_dir = ROOT / "output"
        run_file = output_dir / f"{lesson}-run.txt"
        expected_file = output_dir / f"{lesson}-expected.txt"
        run_file.write_text(actual, encoding="utf-8")
        assert_output_matches(actual, expected_file.read_text(encoding="utf-8"), expected_file)
        print(f"PASS: {lesson} replay matches {expected_file.name}")


if __name__ == "__main__":
    main()
