"""Validate and replay cached structured judgments without a network call."""

from __future__ import annotations

import json
from pathlib import Path

from sys import path

path.insert(0, str(Path(__file__).resolve().parents[1] / "lesson_01_labeled-fixtures"))
from baseline import load_cases  # noqa: E402

REQUIRED = {"case_id", "predicted_pass", "reason"}


def load_judgments(source: Path, case_ids: set[str]) -> dict[str, dict[str, object]]:
    judgments: dict[str, dict[str, object]] = {}
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        item = json.loads(line)
        if not isinstance(item, dict) or set(item) != REQUIRED:
            raise ValueError(f"Line {line_number}: expected keys {sorted(REQUIRED)}.")
        case_id = item["case_id"]
        if not isinstance(case_id, str) or case_id not in case_ids or case_id in judgments:
            raise ValueError(f"Line {line_number}: invalid, unknown, or duplicate case_id.")
        if not isinstance(item["predicted_pass"], bool) or not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError(f"Line {line_number}: verdict must be boolean and reason must be text.")
        judgments[case_id] = item
    if set(judgments) != case_ids:
        raise ValueError(f"Judgment IDs do not match source IDs; missing={sorted(case_ids - set(judgments))}.")
    return judgments


def main() -> None:
    lesson_root = Path(__file__).resolve().parent
    cases = load_cases(lesson_root.parent / "lesson_01_labeled-fixtures" / "cases.jsonl")
    judgments = load_judgments(lesson_root / "cached_judgments.jsonl", {str(case["id"]) for case in cases})
    destination = lesson_root / "judgments.jsonl"
    destination.write_text(
        "".join(json.dumps(judgments[str(case["id"])], sort_keys=True) + "\n" for case in cases),
        encoding="utf-8",
    )
    print(f"PASS: validated {len(judgments)} judgments for {len(cases)} source cases")
    print("Artifact: judgments.jsonl is ready for Lesson 3.")


if __name__ == "__main__":
    main()
