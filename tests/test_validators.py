from __future__ import annotations

import json
import unittest
from pathlib import Path

from agent.schemas import BuildFile, BuildStep, LessonArtifact, LessonSection
from agent.validators import validate_lesson, word_count

ROOT = Path(__file__).resolve().parent.parent


class LessonValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads((ROOT / "agent" / "config.json").read_text(encoding="utf-8"))

    def test_word_count_ignores_inline_html_tags(self) -> None:
        self.assertEqual(word_count("one <strong>two</strong> three"), 3)

    def test_path_traversal_is_rejected(self) -> None:
        from agent.schemas import BuildPlan, LessonPlan, SectionPlan

        plan = LessonPlan(
            number=1,
            slug="seed-eval",
            title="Seed the eval",
            checkpoint_ids=["CP1"],
            sections=[SectionPlan(title="Labels", idea="Explain reliable label policy clearly.", minutes=3)],
            build=BuildPlan(
                title="Seed fixture",
                artifact="A labeled JSONL fixture",
                minutes=15,
                consumes=[],
                produces="build/lesson_01_seed-eval/cases.jsonl",
                visible_checks=["Five valid cases"],
            ),
        )
        prose = "word " * 300
        artifact = LessonArtifact(
            lesson_number=1,
            title="Seed the eval",
            checkpoint_ids=["CP1"],
            sections=[LessonSection(title="Labels", markdown=prose)],
            build_intro="Create a tiny labeled fixture and validate every row before moving on.",
            files=[BuildFile(path="../escape.py", content="print('no')")],
            steps=[
                BuildStep(
                    instruction="Run the fixture validator and inspect the count.",
                    command="python validate.py",
                    expected_check="PASS: 5 cases",
                )
            ],
            expected_output="PASS: 5 cases",
            artifact_contract="build/lesson_01_seed-eval/cases.jsonl",
            summary="The learner created and validated a compact labeled evaluation set.",
        )
        issues = validate_lesson(artifact, plan, self.config, is_final=False)
        self.assertTrue(any("Unsafe build path" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
