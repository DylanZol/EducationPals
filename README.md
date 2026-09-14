# EducationPals AI Engineer take-home

Reproducible setup for generating a text-only, 90-minute course on **Evals and
LLM-as-Judge**. The final capstone is a working grader that reports precision
and recall. Course prose, build-alongs, code artifacts, and generation reviews
are produced by the agent pipeline in `agent/` rather than written by hand.

## Setup status

The submission is complete and runs offline. `course/` contains the generated
lessons, `build/` contains the compounding learner artifacts, and `output/`
contains captured learner run transcripts. The generation setup, prompts,
schemas, validators, and complete sanitized response cache remain in `agent/`
for audit and exact replay.

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
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m agent generate --offline
python scripts\replay_submission.py
python -m agent verify
python -m unittest discover -v
```

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m agent generate --offline
python scripts/replay_submission.py
python -m agent verify
python -m unittest discover -v
```

The offline generation command validates prompt hashes, output hashes, schemas,
and every cached generation stage before recreating the lesson and build files.
The replay script then runs all learner commands in order, writes actual stdout
to `output/lesson-0N-run.txt`, and fails if it differs from the committed
expected output. Neither command requires an API key or network access.

## Generate the course

Set `OPENAI_API_KEY` in your shell, then run:

```bash
python -m agent generate
```

The live run uses the OpenAI Responses API with Pydantic structured outputs,
stores sanitized response envelopes in `agent/cache/`, and writes the rendered
submission to `course/`, `build/`, and `output/`. No API key is written to disk.

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
Git metadata, secrets, and existing archives, then fails if the result is 10 MB
or larger. The sanitized `agent/cache/` records are intentionally included so
the reviewer can reproduce the generated artifacts offline.

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
- Offline generation validates and replays every staged model response without a
  network call or paid API key.
- The submitted learner build replays fixtures and cached structured judgments
  without a network call or paid API key.

The API integration follows the official OpenAI guidance for the Responses API
and [structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
