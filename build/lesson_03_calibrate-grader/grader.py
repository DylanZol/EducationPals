"""Join human labels and cached judge verdicts into a reproducible calibration report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from sys import path

path.insert(0, str(Path(__file__).resolve().parents[1] / "lesson_01_labeled-fixtures"))
from baseline import load_cases  # noqa: E402
path.insert(0, str(Path(__file__).resolve().parents[1] / "lesson_02_judge-contract"))
from judge import load_judgments  # noqa: E402


def rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.3f}" if denominator else "n/a"


def confusion_cells(
    cases: list[dict[str, object]], judgments: dict[str, dict[str, object]]
) -> dict[str, list[str]]:
    cells = {"TP": [], "FP": [], "FN": [], "TN": []}
    for case in cases:
        actual = bool(case["expected_pass"])
        predicted = bool(judgments[str(case["id"])]["predicted_pass"])
        cells["TP" if actual and predicted else "FP" if predicted else "FN" if actual else "TN"].append(
            str(case["id"])
        )
    return cells


def print_matrix(cells: dict[str, list[str]]) -> None:
    print("Confusion matrix (positive = judge approves answer)")
    print(f"TP={len(cells['TP'])}  FP={len(cells['FP'])}  FN={len(cells['FN'])}  TN={len(cells['TN'])}")


def print_metrics(cells: dict[str, list[str]]) -> None:
    print(f"Precision: {rate(len(cells['TP']), len(cells['TP']) + len(cells['FP']))}")
    print(f"Recall:    {rate(len(cells['TP']), len(cells['TP']) + len(cells['FN']))}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--inspect-inputs", action="store_true")
    actions.add_argument("--matrix", action="store_true")
    actions.add_argument("--metrics", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    cases = load_cases(root / "lesson_01_labeled-fixtures" / "cases.jsonl")
    judgments = load_judgments(
        root / "lesson_02_judge-contract" / "judgments.jsonl",
        {str(case["id"]) for case in cases},
    )
    if args.inspect_inputs:
        print(f"PASS: joined {len(cases)} cases with {len(judgments)} judgments")
        return

    cells = confusion_cells(cases, judgments)
    counts = {name: len(ids) for name, ids in cells.items()}
    if sum(counts.values()) != len(cases):
        raise RuntimeError("Confusion matrix count does not equal source case count.")

    if args.matrix:
        print_matrix(cells)
        return

    if args.metrics:
        print_metrics(cells)
        return

    print_matrix(cells)
    print_metrics(cells)
    print(f"False positives: {', '.join(cells['FP']) or 'none'}")
    print(f"False negatives: {', '.join(cells['FN']) or 'none'}")
    print(f"PASS: accounted for {len(cases)} joined cases")


if __name__ == "__main__":
    main()
