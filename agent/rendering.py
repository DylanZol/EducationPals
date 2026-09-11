"""Render validated structured outputs into the required submission layout."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from .schemas import BreakingPoints, CoursePlan, LessonArtifact, ReviewResult


def _safe_destination(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"Unsafe generated path: {relative!r}")
    destination = root.joinpath(*pure.parts).resolve()
    resolved_root = root.resolve()
    if destination != resolved_root and resolved_root not in destination.parents:
        raise ValueError(f"Generated path escaped root: {relative!r}")
    return destination


def _write_text(root: Path, relative: str, content: str) -> str:
    destination = _safe_destination(root, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content.rstrip() + "\n", encoding="utf-8")
    return destination.relative_to(root).as_posix()


def render_plan(root: Path, points: BreakingPoints, plan: CoursePlan) -> str:
    lines = [f"# {plan.title}", "", plan.promise, "", "## Breaking points", ""]
    for point in points.breaking_points:
        lines.extend(
            [
                f"### {point.id}: {point.symptom}",
                "",
                f"**Misconception:** {point.misconception}",
                "",
                f"**Consequence:** {point.consequence}",
                "",
            ]
        )
    lines.extend(["## Checkpoints", ""])
    for checkpoint in plan.checkpoints:
        lines.extend(
            [
                f"- **{checkpoint.id}:** {checkpoint.ability}",
                f"  Evidence: {checkpoint.evidence}",
            ]
        )
    lines.extend(["", "## Backwards lesson plan", ""])
    for lesson in plan.lessons:
        lines.extend(
            [
                f"### Lesson {lesson.number}: {lesson.title}",
                "",
                f"Checkpoints: {', '.join(lesson.checkpoint_ids)}",
                "",
                f"Build: {lesson.build.title} ({lesson.build.minutes} minutes)",
                "",
                f"Consumes: {', '.join(lesson.build.consumes) or 'Nothing; this is the seed artifact.'}",
                "",
                f"Produces: {lesson.build.produces}",
                "",
            ]
        )
    return _write_text(root, "course/00-course-plan.md", "\n".join(lines))


def render_lesson(root: Path, lesson_slug: str, artifact: LessonArtifact) -> list[str]:
    lesson_number = artifact.lesson_number
    course_lines = [
        f"# Lesson {lesson_number}: {artifact.title}",
        "",
        f"Checkpoints: {', '.join(artifact.checkpoint_ids)}",
        "",
    ]
    for section in artifact.sections:
        course_lines.extend([f"## {section.title}", "", section.markdown, ""])
    course_lines.extend(
        [
            "## Build-along",
            "",
            artifact.build_intro,
            "",
            f"Continue in `build/lesson_{lesson_number:02d}_{lesson_slug}/BUILD.md`.",
            "",
            f"Artifact contract for the next lesson: `{artifact.artifact_contract}`",
        ]
    )
    managed = [
        _write_text(
            root,
            f"course/{lesson_number:02d}-{lesson_slug}.md",
            "\n".join(course_lines),
        )
    ]

    build_root = f"build/lesson_{lesson_number:02d}_{lesson_slug}"
    for build_file in artifact.files:
        managed.append(_write_text(root, f"{build_root}/{build_file.path}", build_file.content))

    build_lines = [f"# {artifact.title}: build-along", "", artifact.build_intro, ""]
    for index, step in enumerate(artifact.steps, start=1):
        build_lines.extend(
            [
                f"## Step {index}",
                "",
                step.instruction,
                "",
                "```console",
                step.command,
                "```",
                "",
                "Visible check:",
                "",
                "```text",
                step.expected_check,
                "```",
                "",
            ]
        )
    managed.append(_write_text(root, f"{build_root}/BUILD.md", "\n".join(build_lines)))
    managed.append(
        _write_text(root, f"output/lesson-{lesson_number:02d}-expected.txt", artifact.expected_output)
    )
    return managed


def render_manifest(
    root: Path,
    *,
    model: str,
    offline: bool,
    provider_records: list[dict[str, object]],
    managed_files: list[str],
    reviews: list[ReviewResult],
) -> str:
    manifest = {
        "generator": "agent.orchestrator",
        "model": model,
        "offline_replay": offline,
        "calls": provider_records,
        "managed_files": sorted(managed_files),
        "reviews": [review.model_dump(mode="json") for review in reviews],
    }
    return _write_text(root, "output/generation-manifest.json", json.dumps(manifest, indent=2))
