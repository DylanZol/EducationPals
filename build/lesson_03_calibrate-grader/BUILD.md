# Calibrate the Judge Instead of Trusting It: build-along

The capstone consumes `cases.jsonl` from Lesson 1 and the normalized `judgments.jsonl` generated in Lesson 2. Run the Lesson 2 command first if the judgment artifact is absent.

## Step 1

Check that the two handoff artifacts join before calculating any rates.

```console
python build/lesson_03_calibrate-grader/grader.py --inspect-inputs
```

Visible check:

```text
`PASS: joined 8 cases with 8 judgments`.
```

## Step 2

Build the confusion matrix from the human labels and cached judge decisions.

```console
python build/lesson_03_calibrate-grader/grader.py --matrix
```

Visible check:

```text
Confusion matrix (positive = judge approves answer)
TP=3  FP=1  FN=1  TN=3
```

## Step 3

Calculate precision and recall from the matrix instead of trusting an
unexamined approval count.

```console
python build/lesson_03_calibrate-grader/grader.py --metrics
```

Visible check:

```text
Precision: 0.750
Recall:    0.750
```

## Step 4

Run the full calibration report to identify the specific misleading judgments.

```console
python build/lesson_03_calibrate-grader/grader.py
```

Visible check:

```text
Confusion matrix (positive = judge approves answer)
TP=3  FP=1  FN=1  TN=3
Precision: 0.750
Recall:    0.750
False positives: C06
False negatives: C03
PASS: accounted for 8 joined cases
```
