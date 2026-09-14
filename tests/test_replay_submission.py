from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.replay_submission import ROOT, assert_output_matches


class ReplaySubmissionTests(unittest.TestCase):
    def test_replay_matches_expected_fixtures(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/replay_submission.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "PASS: lesson-01 replay matches lesson-01-expected.txt\n"
            "PASS: lesson-02 replay matches lesson-02-expected.txt\n"
            "PASS: lesson-03 replay matches lesson-03-expected.txt\n",
        )

    def test_replay_rejects_mismatched_output(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Output did not match"):
            assert_output_matches("actual\n", "expected\n", ROOT / "output" / "lesson-01-expected.txt")

    def test_capstone_output_is_exact(self) -> None:
        completed = subprocess.run(
            [sys.executable, "build/lesson_03_calibrate-grader/grader.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        expected = (ROOT / "output" / "lesson-03-capstone-expected.txt").read_text(encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, expected)


if __name__ == "__main__":
    unittest.main()
