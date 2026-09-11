# Source brief normalized for the generation agents

## Deliverable

Generate a text-only course that takes a learner about 90 minutes and has two or
three lessons. Each lesson may have at most five sections, with each section
covering one idea in 300–500 words (about 2–3 minutes). Every lesson ends with
one interactive build-along under 20 minutes. The build artifacts must compound:
lesson one's output is lesson two's input, and the final artifact is the
capstone.

## Required design order

1. Identify at least three real breaking points before generating lesson content.
2. Convert them into observable checkpoints: things the learner can now do.
3. Work backwards from the capstone into independently useful artifacts.
4. Generate lessons in prerequisite order.
5. Critique every generated lesson against the constraints before accepting it.

## Build rules

- Use a CLI or notebook that prints a visible check at every incremental step.
- Keep industry-standard vocabulary.
- Use only text, inline HTML, or SVG; do not use raster images or Mermaid.
- Do not add quizzes, flashcards, assessments, video, or audio.
- Keep the final zip under 10 MB and do not include dependencies or model weights.
- The build must run offline for review using fixtures or cached model results.
- Python must be 3.12 and dependencies must be listed in `requirements.txt`.

## Review priority

Build correctness and compounding artifacts come first. Then checkpoint quality,
prerequisite order, technical accuracy, and generation traceability. Prose polish
is deliberately not the optimization target.
