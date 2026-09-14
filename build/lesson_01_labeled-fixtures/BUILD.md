# Make a Small Eval Set Comparable: build-along

This lesson creates the source artifact for the course. The fixture is checked
in so you can focus on inspecting the contract before changing data.

## Step 1

Inspect one JSONL record. Notice that `expected_pass` is a boolean human label,
not a score invented by the judge.

```console
python -c "import json; print(json.loads(open('build/lesson_01_labeled-fixtures/cases.jsonl', encoding='utf-8').readline()))"
```

Visible check: the printed record has `id`, `prompt`, `answer`, `rubric`, and
`expected_pass`.

## Step 2

Run the baseline validator.

```console
python build/lesson_01_labeled-fixtures/baseline.py
```

Visible check:

```text
PASS: 8 valid cases (4 expected pass, 4 expected fail)
Artifact: cases.jsonl is ready for Lesson 2.
```
