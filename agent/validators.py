"""Deterministic checks that run in addition to the model critic."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from .schemas import BreakingPoints, CoursePlan, LessonArtifact, LessonPlan


def word_count(markdown: str) -> int:
    without_tags = re.sub(r"<[^>]+>", " ", markdown)
    return len(re.findall(r"\b[\w'-]+\b", without_tags))


def validate_breaking_points(points: BreakingPoints) -> list[str]:
    issues: list[str] = []
    ids = [point.id for point in points.breaking_points]
    if len(ids) != len(set(ids)):
        issues.append("Breaking-point IDs must be unique.")
    return issues


def validate_plan(plan: CoursePlan, config: dict[str, object], points: BreakingPoints) -> list[str]:
    submission = config["submission"]
    assert isinstance(submission, dict)
    issues: list[str] = []
    lesson_count = int(submission["lesson_count"])
    max_sections = int(submission["max_sections_per_lesson"])
    max_build = int(submission["build_minutes_max"])

    if len(plan.lessons) != lesson_count:
        issues.append(f"Expected exactly {lesson_count} lessons; got {len(plan.lessons)}.")
    if [lesson.number for lesson in plan.lessons] != list(range(1, len(plan.lessons) + 1)):
        issues.append("Lesson numbers must be contiguous and start at 1.")

    checkpoint_ids = [checkpoint.id for checkpoint in plan.checkpoints]
    if len(checkpoint_ids) != len(set(checkpoint_ids)):
        issues.append("Checkpoint IDs must be unique.")
    breaking_ids = {point.id for point in points.breaking_points}
    for checkpoint in plan.checkpoints:
        unknown = set(checkpoint.breaking_point_ids) - breaking_ids
        if unknown:
            issues.append(f"{checkpoint.id} references unknown breaking points: {sorted(unknown)}.")

    assigned: list[str] = []
    prior_artifact: str | None = None
    for lesson in plan.lessons:
        if len(lesson.sections) > max_sections:
            issues.append(f"Lesson {lesson.number} exceeds {max_sections} sections.")
        if lesson.build.minutes > max_build:
            issues.append(f"Lesson {lesson.number} build exceeds {max_build} minutes.")
        unknown = set(lesson.checkpoint_ids) - set(checkpoint_ids)
        if unknown:
            issues.append(f"Lesson {lesson.number} references unknown checkpoints: {sorted(unknown)}.")
        assigned.extend(lesson.checkpoint_ids)
        if lesson.number == 1 and lesson.build.consumes:
            issues.append("Lesson 1 must not claim a prior generated artifact.")
        if lesson.number > 1 and prior_artifact not in lesson.build.consumes:
            issues.append(
                f"Lesson {lesson.number} must consume prior artifact {prior_artifact!r}."
            )
        prior_artifact = lesson.build.produces

    missing = set(checkpoint_ids) - set(assigned)
    if missing:
        issues.append(f"Unassigned checkpoints: {sorted(missing)}.")
    if len(assigned) != len(set(assigned)):
        issues.append("Each checkpoint must be assigned to exactly one lesson.")
    final_checks = " ".join(plan.lessons[-1].build.visible_checks).lower()
    for required in ("confusion matrix", "precision", "recall"):
        if required not in final_checks:
            issues.append(f"Final build is missing visible check: {required}.")
    return issues


def validate_lesson(
    artifact: LessonArtifact,
    lesson_plan: LessonPlan,
    config: dict[str, object],
    *,
    is_final: bool,
) -> list[str]:
    submission = config["submission"]
    assert isinstance(submission, dict)
    allowed = set(config["allowed_build_extensions"])
    issues: list[str] = []

    if artifact.lesson_number != lesson_plan.number:
        issues.append("Generated lesson number does not match the plan.")
    if artifact.checkpoint_ids != lesson_plan.checkpoint_ids:
        issues.append("Generated checkpoint IDs do not exactly match the plan.")
    if artifact.artifact_contract != lesson_plan.build.produces:
        issues.append("Generated artifact contract does not match the planned output.")
    if len(artifact.sections) != len(lesson_plan.sections):
        issues.append("Generated section count does not match the plan.")

    minimum = int(submission["section_word_min"])
    maximum = int(submission["section_word_max"])
    for index, section in enumerate(artifact.sections, start=1):
        count = word_count(section.markdown)
        if not minimum <= count <= maximum:
            issues.append(
                f"Lesson {lesson_plan.number} section {index} has {count} words; expected {minimum}-{maximum}."
            )

    seen_paths: set[str] = set()
    for build_file in artifact.files:
        path = PurePosixPath(build_file.path)
        normalized = path.as_posix()
        if path.is_absolute() or ".." in path.parts or normalized.startswith("/"):
            issues.append(f"Unsafe build path: {build_file.path!r}.")
        if path.suffix.lower() not in allowed:
            issues.append(f"Disallowed build extension: {build_file.path!r}.")
        if normalized.lower() in {"build.md", ".env"}:
            issues.append(f"Reserved build path: {build_file.path!r}.")
        if normalized in seen_paths:
            issues.append(f"Duplicate build path: {build_file.path!r}.")
        if len(build_file.content.encode("utf-8")) > 250_000:
            issues.append(f"Build file exceeds 250 KB: {build_file.path!r}.")
        seen_paths.add(normalized)

    combined = "\n".join(section.markdown for section in artifact.sections).lower()
    for prohibited in ("```mermaid", ".png", ".jpeg", ".jpg", "flashcard", "quiz"):
        if prohibited in combined:
            issues.append(f"Prohibited course content found: {prohibited!r}.")
    if is_final:
        final_text = (artifact.expected_output + "\n" + combined).lower()
        for required in ("precision", "recall"):
            if required not in final_text:
                issues.append(f"Final lesson output does not mention {required}.")
    return issues
