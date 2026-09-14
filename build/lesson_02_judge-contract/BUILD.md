# Replay an LLM Judge with a Contract: build-along

The cached JSONL represents structured output captured from a judge. A live
implementation would validate a provider response at this same boundary and
cache the normalized records for replay.

## Step 1

Re-run the source-fixture validator. Lesson 2 consumes this exact artifact.

```console
python build/lesson_01_labeled-fixtures/baseline.py
```

Visible check: `PASS: 8 valid cases (4 expected pass, 4 expected fail)`.

## Step 2

Validate coverage, types, and IDs, then write the normalized judgment artifact.

```console
python build/lesson_02_judge-contract/judge.py
```

Visible check:

```text
PASS: validated 8 judgments for 8 source cases
Artifact: judgments.jsonl is ready for Lesson 3.
```
