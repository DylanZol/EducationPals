from __future__ import annotations

import json
import unittest
from pathlib import Path

from agent.orchestrator import render_prompt

ROOT = Path(__file__).resolve().parent.parent


class SetupContractTests(unittest.TestCase):
    def test_assignment_limits_are_encoded(self) -> None:
        config = json.loads((ROOT / "agent" / "config.json").read_text(encoding="utf-8"))
        submission = config["submission"]
        self.assertIn(submission["lesson_count"], (2, 3))
        self.assertLessEqual(submission["max_sections_per_lesson"], 5)
        self.assertEqual((submission["section_word_min"], submission["section_word_max"]), (300, 500))
        self.assertLessEqual(submission["build_minutes_max"], 20)

    def test_prompt_renderer_rejects_unresolved_variables(self) -> None:
        with self.assertRaises(ValueError):
            render_prompt("00_breaking_points.md", {"TOPIC": "Evals"})


if __name__ == "__main__":
    unittest.main()
