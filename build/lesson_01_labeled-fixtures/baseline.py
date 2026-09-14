"""Build and validate the seed evaluation fixture used by later lessons."""

from __future__ import annotations

import argparse
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


def report_balance(cases: list[dict[str, object]], label: str) -> None:
    passed = sum(case["expected_pass"] for case in cases)
    print(f"PASS: {len(cases)} valid {label} ({passed} expected pass, {len(cases) - passed} expected fail)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--inspect-starter", action="store_true")
    actions.add_argument("--validate-starter", action="store_true")
    actions.add_argument("--write-cases", action="store_true")
    args = parser.parse_args()

    lesson_root = Path(__file__).resolve().parent
    starter = lesson_root / "cases.starter.jsonl"
    destination = lesson_root / "cases.jsonl"

    if args.inspect_starter:
        first_case = load_cases(starter)[0]
        print(f"PASS: starter contract has {len(REQUIRED)} required fields")
        print(f"First case: {first_case['id']} (expected_pass={first_case['expected_pass']})")
        return

    if args.validate_starter:
        report_balance(load_cases(starter), "starter cases")
        return

    if args.write_cases:
        cases = load_cases(starter)
        destination.write_text(
            "".join(json.dumps(case, separators=(",", ":")) + "\n" for case in cases),
            encoding="utf-8",
        )
        print(f"PASS: wrote {len(cases)} normalized cases to cases.jsonl")
        return

    report_balance(load_cases(destination), "cases")
    print("Artifact: cases.jsonl is ready for Lesson 2.")


if __name__ == "__main__":
    main()
