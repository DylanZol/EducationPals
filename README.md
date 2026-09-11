# EducationPals AI Engineer take-home

Reproducible setup for generating a text-only, 90-minute course on **Evals and
LLM-as-Judge**. The final capstone is a working grader that reports precision
and recall. Course prose, build-alongs, code artifacts, and generation reviews
are produced by the agent pipeline in `agent/` rather than written by hand.

## Setup status

The repository scaffold and orchestration are ready. `course/`, `build/`, and
`output/` intentionally contain setup markers until the first live generation
run is reviewed. After that run, commit the generated files and `agent/cache/`
so reviewers can replay the exact responses without an API key.

## Why this topic and shape

The topic has an objective terminal check: the learner's final CLI can be run
against labeled cases and its confusion matrix, precision, and recall can be
verified. The configured three-lesson sequence makes each build output useful
on its own and passes it forward:

1. A labeled eval fixture and deterministic baseline.
2. A schema-validated LLM judge plus cached judgments.
3. A calibrated grader CLI that prints precision and recall.

The pipeline does not write lesson content until it has first generated explicit
breaking points, converted those into observable checkpoints, and designed the
course backwards from the capstone.

## Run with Python 3.12

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m agent verify
```

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m agent verify
```

`verify` is offline and checks the repository contract, config, prompts, and any
generated artifacts already present.

## Generate the course

Set `OPENAI_API_KEY` in your shell, then run:

```bash
python -m agent generate
```

The live run uses the OpenAI Responses API with Pydantic structured outputs,
stores sanitized response envelopes in `agent/cache/`, and writes the rendered
submission to `course/`, `build/`, and `output/`. No API key is written to disk.

To replay the cached model results without a network call:

```bash
python -m agent generate --offline
```

To inspect the generation plan without touching course/build outputs:

```bash
python -m agent show-plan
```

## Package the final submission

After completing `writeup.md` and verifying the generated build-alongs, create
the reviewer zip with the required top-level name:

```bash
python scripts/package_submission.py lastname-firstname
```

The packager writes `dist/lastname-firstname.zip`, excludes local environments,
Git metadata, caches, secrets, and existing archives, then fails if the result is
10 MB or larger.

## Required submission layout

```text
educationpals-course-takehome/
  README.md
  course/       # generated lesson Markdown, one file per lesson
  build/        # generated learner code, one folder per build-along
  output/       # captured CLI output and generation manifest
  agent/        # config, prompts, orchestration, schemas, cached responses
  writeup.md    # added after the final course review
```


## Generation invariants

- Exactly three lessons, at most five sections each.
- Every prose section targets 300–500 words and one idea.
- One build-along per lesson, under 20 minutes.
- Lesson `N` consumes the artifact produced by lesson `N-1`.
- Every build step includes a command and a visible expected check.
- The final build prints a confusion matrix, precision, and recall.
- Generated file paths are confined to their assigned lesson folder.
- Live responses are stored with `store=False`; only sanitized parsed output and
  token usage are cached locally.

The API integration follows the official OpenAI guidance for the Responses API
and [structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
