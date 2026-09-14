"""Join human labels and cached judge verdicts into a reproducible calibration report."""

from __future__ import annotations

import json
from pathlib import Path
from sys import path

path.insert(0, str(Path(__file__).resolve().parents[1] / "lesson_01_labeled-fixtures"))
from baseline import load_cases  # noqa: E402
path.insert(0, str(Path(__file__).resolve().parents[1] / "lesson_02_judge-contract"))
from judge import load_judgments  # noqa: E402


def rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.3f}" if denominator else "n/a"


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cases = load_cases(root / "lesson_01_labeled-fixtures" / "cases.jsonl")
    judgments = load_judgments(
        root / "lesson_02_judge-contract" / "judgments.jsonl",
        {str(case["id"]) for case in cases},
    )
    cells = {"TP": [], "FP": [], "FN": [], "TN": []}
    for case in cases:
        actual = bool(case["expected_pass"])
        predicted = bool(judgments[str(case["id"])]["predicted_pass"])
        cells["TP" if actual and predicted else "FP" if predicted else "FN" if actual else "TN"].append(str(case["id"]))
    counts = {name: len(ids) for name, ids in cells.items()}
    if sum(counts.values()) != len(cases):
        raise RuntimeError("Confusion matrix count does not equal source case count.")
    print("Confusion matrix (positive = judge approves answer)")
    print(f"TP={counts['TP']}  FP={counts['FP']}  FN={counts['FN']}  TN={counts['TN']}")
    print(f"Precision: {rate(counts['TP'], counts['TP'] + counts['FP'])}")
    print(f"Recall:    {rate(counts['TP'], counts['TP'] + counts['FN'])}")
    print(f"False positives: {', '.join(cells['FP']) or 'none'}")
    print(f"False negatives: {', '.join(cells['FN']) or 'none'}")
    print(f"PASS: accounted for {len(cases)} joined cases")


if __name__ == "__main__":
    main()
