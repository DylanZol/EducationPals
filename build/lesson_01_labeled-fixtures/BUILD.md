# Make a Small Eval Set Comparable: build-along

This lesson creates the source artifact for the course. The fixture is checked in so you can focus on inspecting the contract before changing data.

## Step 1

Inspect the starter contract before trusting its labels. `expected_pass` is a
boolean human label, not a score invented by a judge.

```console
python build/lesson_01_labeled-fixtures/baseline.py --inspect-starter
```

Visible check:

```text
PASS: starter contract has 5 required fields
First case: C01 (expected_pass=True)
```

## Step 2

Validate the raw records and their pass/fail balance before producing an
artifact for another lesson.

```console
python build/lesson_01_labeled-fixtures/baseline.py --validate-starter
```

Visible check:

```text
PASS: 8 valid starter cases (4 expected pass, 4 expected fail)
```

## Step 3

Normalize the validated starter records into the lesson handoff artifact.

```console
python build/lesson_01_labeled-fixtures/baseline.py --write-cases
```

Visible check:

```text
PASS: wrote 8 normalized cases to cases.jsonl
```

## Step 4

Validate the produced artifact exactly as Lesson 2 will consume it.

```console
python build/lesson_01_labeled-fixtures/baseline.py
```

Visible check:

```text
PASS: 8 valid cases (4 expected pass, 4 expected fail)
Artifact: cases.jsonl is ready for Lesson 2.
```
