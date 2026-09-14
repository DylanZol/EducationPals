"""Validate the seed evaluation fixture and report its label balance."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED = {"id", "prompt", "answer", "rubric", "expected_pass"}


def load_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        item = json.loads(line)
        if not isinstance(item, dict) or set(item) != REQUIRED:
            raise ValueError(f"Line {line_number}: expected keys {sorted(REQUIRED)}.")
        case_id = item["id"]
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"Line {line_number}: ID must be unique and non-empty.")
        if not isinstance(item["expected_pass"], bool):
            raise ValueError(f"Line {line_number}: expected_pass must be boolean.")
        if any(not isinstance(item[key], str) or not item[key].strip() for key in REQUIRED - {"expected_pass"}):
            raise ValueError(f"Line {line_number}: text fields must be non-empty strings.")
        seen.add(case_id)
        cases.append(item)
    if not cases or not any(case["expected_pass"] for case in cases) or not any(not case["expected_pass"] for case in cases):
        raise ValueError("Fixture needs at least one passing and one failing case.")
    return cases


def main() -> None:
    cases = load_cases(Path(__file__).with_name("cases.jsonl"))
    passed = sum(case["expected_pass"] for case in cases)
    print(f"PASS: {len(cases)} valid cases ({passed} expected pass, {len(cases) - passed} expected fail)")
    print("Artifact: cases.jsonl is ready for Lesson 2.")


if __name__ == "__main__":
    main()
