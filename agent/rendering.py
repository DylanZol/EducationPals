"""Render validated structured outputs into the required submission layout."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path, PurePosixPath

from .schemas import BreakingPoints, CoursePlan, LessonArtifact, ReviewResult

FLOW_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 140" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Course artifact data flow</title>
  <desc id="flow-desc">Human-labeled cases flow to a validated judge replay, then both flow to the calibrated grader.</desc>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8Z" fill="#334155"/></marker></defs>
  <rect x="12" y="38" width="190" height="64" rx="8" fill="#e0f2fe" stroke="#0369a1"/><text x="107" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0c4a6e">Lesson 1</text><text x="107" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#0c4a6e">cases.jsonl + gold labels</text>
  <path d="M202,70 H266" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="270" y="38" width="180" height="64" rx="8" fill="#fef3c7" stroke="#b45309"/><text x="360" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#78350f">Lesson 2</text><text x="360" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#78350f">judgments.jsonl</text>
  <path d="M450,70 H514" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="518" y="38" width="190" height="64" rx="8" fill="#dcfce7" stroke="#15803d"/><text x="613" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#14532d">Lesson 3 capstone</text><text x="613" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#14532d">matrix, precision, recall</text>
</svg>"""


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
    lines.extend(
        [
            "",
            "## Pacing and artifact flow",
            "",
            "Each lesson is **30 minutes**: four focused prose sections of **3 minutes each**",
            "(12 minutes total), followed by one **18-minute build-along**. The three builds",
            "remain cumulative: each creates the checked artifact consumed by the next lesson",
            "and preserves the final offline grader capstone.",
            "",
            FLOW_SVG,
            "",
            "## Backwards lesson plan",
            "",
        ]
    )
    for lesson in plan.lessons:
        lines.extend(
            [
                f"### Lesson {lesson.number}: {lesson.title}",
                "",
                lesson.summary,
                "",
                "Pacing: 3 min x 4 prose sections, then an 18-minute build (30 minutes total).",
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
        "**Pacing:** Four 3-minute prose sections (12 minutes), then an 18-minute",
        "build-along (30 minutes total).",
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
        _write_text(
            root,
            f"output/lesson-{lesson_number:02d}-expected.txt",
            artifact.expected_output,
        )
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
        "schema_version": 2,
        "generator": "agent.orchestrator",
        "model": model,
        "mode": "offline-cache-replay" if offline else "live-api",
        "offline_replay": offline,
        "provider_records": provider_records,
        "managed_files": [
            {
                "path": relative,
                "sha256": sha256(_safe_destination(root, relative).read_bytes()).hexdigest(),
            }
            for relative in sorted(managed_files)
        ],
        "reviews": [review.model_dump(mode="json") for review in reviews],
    }
    return _write_text(root, "output/generation-manifest.json", json.dumps(manifest, indent=2))
