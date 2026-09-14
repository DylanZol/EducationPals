"""Auditable, staged course generation and offline replay."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .providers import CacheStore, CachedProvider, OpenAIProvider
from .rendering import render_lesson, render_plan
from .schemas import BreakingPoints, CoursePlan, LessonArtifact, ReviewResult
from .validators import validate_breaking_points, validate_lesson, validate_plan

ROOT = Path(__file__).resolve().parent.parent
AGENT_ROOT = ROOT / "agent"


def load_config() -> dict[str, Any]:
    return json.loads((AGENT_ROOT / "config.json").read_text(encoding="utf-8"))


def render_prompt(filename: str, values: dict[str, object]) -> str:
    prompt = (AGENT_ROOT / "prompts" / filename).read_text(encoding="utf-8")
    for key, value in values.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
    if "{{" in prompt or "}}" in prompt:
        raise ValueError(f"Unresolved placeholder in {filename}")
    return prompt


def _base_values(config: dict[str, Any]) -> dict[str, object]:
    submission = config["submission"]
    return {
        "TOPIC": submission["topic"],
        "AUDIENCE": submission["audience"],
        "CAPSTONE": submission["capstone"],
        "LEARNER_MINUTES": submission["learner_minutes"],
        "LESSON_COUNT": submission["lesson_count"],
        "MAX_SECTIONS": submission["max_sections_per_lesson"],
        "MAX_BUILD_MINUTES": submission["build_minutes_max"],
    }


def _provider(config: dict[str, Any], *, offline: bool) -> CachedProvider | OpenAIProvider:
    cache = CacheStore(AGENT_ROOT / "cache")
    if offline:
        return CachedProvider(cache)
    configured_model = str(config["generation"]["model"])
    model = os.environ.get("EDUCATIONPALS_MODEL", configured_model)
    return OpenAIProvider(cache, model)


def _raise_for_issues(stage: str, issues: list[str]) -> None:
    if issues:
        rendered = "\n".join(f"- {issue}" for issue in issues)
        raise RuntimeError(f"{stage} failed deterministic validation:\n{rendered}")


def _generate_foundations(
    provider: CachedProvider | OpenAIProvider,
    config: dict[str, Any],
) -> tuple[BreakingPoints, CoursePlan]:
    base = _base_values(config)
    breaking_prompt = render_prompt("00_breaking_points.md", base)
    points = provider.generate("00-breaking-points", breaking_prompt, BreakingPoints)
    _raise_for_issues("Breaking points", validate_breaking_points(points))

    plan_prompt = render_prompt(
        "10_course_plan.md",
        {
            **base,
            "BREAKING_POINTS": json.dumps(points.model_dump(mode="json"), indent=2),
        },
    )
    plan = provider.generate("10-course-plan", plan_prompt, CoursePlan)
    _raise_for_issues("Course plan", validate_plan(plan, config, points))
    return points, plan


def generate(*, offline: bool) -> None:
    config = load_config()
    provider = _provider(config, offline=offline)
    points, plan = _generate_foundations(provider, config)
    base = _base_values(config)
    prior_context: list[dict[str, str]] = []
    accepted: list[LessonArtifact] = []
    reviews: list[ReviewResult] = []
    max_revisions = int(config["generation"]["max_revision_rounds"])

    for lesson_plan in plan.lessons:
        lesson_number = lesson_plan.number
        lesson_prompt = render_prompt(
            "20_lesson.md",
            {
                **base,
                "LESSON_NUMBER": lesson_number,
                "COURSE_PLAN": json.dumps(plan.model_dump(mode="json"), indent=2),
                "PRIOR_CONTEXT": json.dumps(prior_context, indent=2),
            },
        )
        candidate = provider.generate(
            f"20-lesson-{lesson_number:02d}-r0",
            lesson_prompt,
            LessonArtifact,
        )

        for revision_round in range(max_revisions + 1):
            deterministic = validate_lesson(
                candidate,
                lesson_plan,
                config,
                is_final=lesson_number == len(plan.lessons),
            )
            review_prompt = render_prompt(
                "30_review.md",
                {
                    "COURSE_PLAN": json.dumps(plan.model_dump(mode="json"), indent=2),
                    "LESSON": json.dumps(candidate.model_dump(mode="json"), indent=2),
                },
            )
            review = provider.generate(
                f"30-review-{lesson_number:02d}-r{revision_round}",
                review_prompt,
                ReviewResult,
            )
            combined_issues = [*deterministic, *review.blocking_issues]
            if review.passed and not combined_issues:
                accepted.append(candidate)
                reviews.append(review)
                prior_context.append(
                    {
                        "summary": candidate.summary,
                        "artifact_contract": candidate.artifact_contract,
                    }
                )
                break
            if revision_round == max_revisions:
                rendered = "\n".join(f"- {issue}" for issue in combined_issues)
                raise RuntimeError(
                    f"Lesson {lesson_number} still has blocking issues after "
                    f"{max_revisions} revision round(s):\n{rendered}"
                )
            revision_prompt = render_prompt(
                "40_revise.md",
                {
                    "COURSE_PLAN": json.dumps(plan.model_dump(mode="json"), indent=2),
                    "LESSON": json.dumps(candidate.model_dump(mode="json"), indent=2),
                    "REVIEW": json.dumps(
                        {
                            "deterministic_issues": deterministic,
                            "critic": review.model_dump(mode="json"),
                        },
                        indent=2,
                    ),
                },
            )
            candidate = provider.generate(
                f"40-revise-{lesson_number:02d}-r{revision_round + 1}",
                revision_prompt,
                LessonArtifact,
            )
        else:  # pragma: no cover - loop always breaks or raises
            raise AssertionError("unreachable")

    managed_files = [render_plan(ROOT, points, plan)]
    for lesson_plan, artifact in zip(plan.lessons, accepted, strict=True):
        managed_files.extend(render_lesson(ROOT, lesson_plan.slug, artifact))

    manifest = {
        "topic": config["submission"]["topic"],
        "mode": "offline-cache-replay" if offline else "live-api",
        "managed_files": managed_files,
        "provider_records": provider.records,
        "reviews": [review.model_dump(mode="json") for review in reviews],
    }
    (ROOT / "output" / "generation-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Generated {len(accepted)} lessons in "
        f"{'offline replay' if offline else 'live API'} mode."
    )
    print("Run `python -m agent verify` before committing the generated artifacts.")


def show_plan() -> None:
    config = load_config()
    provider = _provider(config, offline=True)
    points, plan = _generate_foundations(provider, config)
    print(
        json.dumps(
            {
                "breaking_points": points.model_dump(mode="json"),
                "course_plan": plan.model_dump(mode="json"),
            },
            indent=2,
        )
    )


def verify() -> None:
    config = load_config()
    required = [
        "README.md",
        "requirements.txt",
        ".python-version",
        "course",
        "build",
        "output",
        "agent/config.json",
        "agent/brief.md",
        "agent/prompts/00_breaking_points.md",
        "agent/prompts/10_course_plan.md",
        "agent/prompts/20_lesson.md",
        "agent/prompts/30_review.md",
        "agent/prompts/40_revise.md",
    ]
    failures = [f"Missing required path: {relative}" for relative in required if not (ROOT / relative).exists()]

    if sys.version_info[:2] != (3, 12):
        failures.append(f"Python 3.12 required; running {sys.version.split()[0]}.")
    submission = config["submission"]
    if int(submission["lesson_count"]) not in (2, 3):
        failures.append("lesson_count must be 2 or 3.")
    if int(submission["max_sections_per_lesson"]) > 5:
        failures.append("max_sections_per_lesson must not exceed 5.")
    if int(submission["build_minutes_max"]) > 20:
        failures.append("build_minutes_max must not exceed 20.")
    if int(submission["section_word_min"]) != 300 or int(submission["section_word_max"]) != 500:
        failures.append("Section word range must be exactly 300-500.")

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    unpinned = [line for line in requirements if line.strip() and "==" not in line]
    if unpinned:
        failures.append(f"Unpinned dependencies: {unpinned}.")

    cache_files = sorted((AGENT_ROOT / "cache").glob("*.json"))
    generated_lessons = sorted((ROOT / "course").glob("[0-9][0-9]-*.md"))
    manifest_path = ROOT / "output" / "generation-manifest.json"
    committed_submission = False
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            committed_submission = (
                manifest.get("mode") == "committed AI-generated submission"
                and manifest.get("generation_method") == "staged prompt orchestration in agent/"
            )
        except json.JSONDecodeError:
            failures.append("output/generation-manifest.json is not valid JSON.")
    if generated_lessons and not cache_files and not committed_submission:
        failures.append(
            "Generated lessons need agent/cache replay files or a committed generation manifest."
        )
    if generated_lessons and not manifest_path.exists():
        failures.append("Generated lessons exist without output/generation-manifest.json.")

    status = [
        "EducationPals repository verification",
        f"Python: {sys.version.split()[0]}",
        f"Topic: {submission['topic']}",
        f"Configured lessons: {submission['lesson_count']}",
        f"Cached model responses: {len(cache_files)}",
        f"Generated lessons: {len(generated_lessons)}",
        f"Result: {'FAIL' if failures else 'PASS'}",
    ]
    if failures:
        status.extend(f"- {failure}" for failure in failures)
    rendered = "\n".join(status) + "\n"
    (ROOT / "output").mkdir(parents=True, exist_ok=True)
    (ROOT / "output" / "setup-check.txt").write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if failures:
        raise SystemExit(1)
