# Replay an LLM Judge with a Contract: build-along

The cached JSONL represents structured output captured from a judge. A live implementation would validate a provider response at this same boundary and cache the normalized records for replay.

## Step 1

Confirm the source artifact exposes the case IDs that every judgment must
cover.

```console
python build/lesson_02_judge-contract/judge.py --inspect-source
```

Visible check:

```text
`PASS: source cases.jsonl provides 8 case IDs`.
```

## Step 2

Validate the cached structured response against those case IDs. This is the
same contract boundary where a live provider response would be checked.

```console
python build/lesson_02_judge-contract/judge.py --validate-cache
```

Visible check:

```text
`PASS: cached judgments cover 8 source cases`.
```

## Step 3

Write the validated, normalized judgments that the capstone can replay without
a network call.

```console
python build/lesson_02_judge-contract/judge.py --write-judgments
```

Visible check:

```text
`PASS: wrote 8 normalized judgments to judgments.jsonl`.
```

## Step 4

Validate the persisted handoff exactly as Lesson 3 will read it.

```console
python build/lesson_02_judge-contract/judge.py --validate-output
```

Visible check:

```text
PASS: validated 8 judgments for 8 source cases
Artifact: judgments.jsonl is ready for Lesson 3.
```
