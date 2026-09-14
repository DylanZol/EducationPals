"""Strict structured-output contracts shared by live and cached providers."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BreakingPoint(StrictModel):
    id: str = Field(pattern=r"^BP[1-9][0-9]*$")
    symptom: str = Field(min_length=20)
    misconception: str = Field(min_length=20)
    consequence: str = Field(min_length=20)


class BreakingPoints(StrictModel):
    breaking_points: list[BreakingPoint] = Field(min_length=3, max_length=5)


class Checkpoint(StrictModel):
    id: str = Field(pattern=r"^CP[1-9][0-9]*$")
    breaking_point_ids: list[str] = Field(min_length=1)
    ability: str = Field(min_length=20)
    evidence: str = Field(min_length=20)


class SectionPlan(StrictModel):
    title: str = Field(min_length=3)
    idea: str = Field(min_length=20)
    minutes: Annotated[int, Field(ge=2, le=3)]


class BuildPlan(StrictModel):
    title: str = Field(min_length=3)
    artifact: str = Field(min_length=10)
    minutes: Annotated[int, Field(ge=5, le=20)]
    consumes: list[str]
    produces: str = Field(min_length=3)
    visible_checks: list[str] = Field(min_length=1)


class LessonPlan(StrictModel):
    number: Annotated[int, Field(ge=1, le=3)]
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=3)
    checkpoint_ids: list[str] = Field(min_length=1, max_length=3)
    sections: list[SectionPlan] = Field(min_length=1, max_length=5)
    build: BuildPlan
    summary: str = Field(default="", min_length=20)


class CoursePlan(StrictModel):
    title: str = Field(min_length=3)
    promise: str = Field(min_length=20)
    checkpoints: list[Checkpoint] = Field(min_length=3)
    lessons: list[LessonPlan] = Field(min_length=2, max_length=3)


class LessonSection(StrictModel):
    title: str = Field(min_length=3)
    markdown: str = Field(min_length=100)


class BuildFile(StrictModel):
    path: str = Field(min_length=1)
    content: str


class BuildStep(StrictModel):
    instruction: str = Field(min_length=10)
    command: str = Field(min_length=1)
    expected_check: str = Field(min_length=3)


class LessonArtifact(StrictModel):
    lesson_number: Annotated[int, Field(ge=1, le=3)]
    title: str = Field(min_length=3)
    checkpoint_ids: list[str] = Field(min_length=1, max_length=3)
    sections: list[LessonSection] = Field(min_length=1, max_length=5)
    build_intro: str = Field(min_length=50)
    files: list[BuildFile] = Field(min_length=1)
    steps: list[BuildStep] = Field(min_length=1)
    expected_output: str = Field(min_length=3)
    artifact_contract: str = Field(min_length=3)
    summary: str = Field(min_length=20)


class ReviewResult(StrictModel):
    passed: bool
    blocking_issues: list[str]
    non_blocking_notes: list[str]
