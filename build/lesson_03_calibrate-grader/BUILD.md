# Calibrate the Judge Instead of Trusting It: build-along

The capstone consumes `cases.jsonl` from Lesson 1 and the normalized
`judgments.jsonl` generated in Lesson 2. Run the Lesson 2 command first if the
judgment artifact is absent.

## Step 1

Generate the validated judgment artifact.

```console
python build/lesson_02_judge-contract/judge.py
```

Visible check: `PASS: validated 8 judgments for 8 source cases`.

## Step 2

Join the human labels and judge predictions and print the calibration report.

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
