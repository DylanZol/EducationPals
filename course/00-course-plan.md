# Evals and LLM-as-Judge: A Grader You Can Trust

This course is for an engineer who has already shipped an AI feature and needs
an answer to a more useful question than "did the last demo look good?" In about
90 minutes, you will create a small, reproducible evaluation harness and use it
to measure an offline replay of an LLM judge. The capstone prints a confusion
matrix, precision, and recall against human labels.

## Breaking points

### BP1: A plausible example is mistaken for an evaluation set

**Misconception:** A few hand-picked prompts can represent production quality.

**Consequence:** Regressions hide in the failure modes that were not written
down, and two runs cannot be compared fairly.

### BP2: Judge output is treated as self-validating

**Misconception:** If a model returns a confident explanation, its verdict has a
usable contract.

**Consequence:** Prose, missing fields, and changed label meanings silently
break downstream metrics.

### BP3: Agreement is reported without the direction of the mistakes

**Misconception:** A single accuracy number explains whether a judge is safe.

**Consequence:** A judge that approves bad answers or rejects useful answers
can look acceptable while hurting the product.

## Checkpoints

- **CP1:** Define a compact evaluation case with a human gold label, a rubric,
  and a stable ID. Evidence: a validator rejects malformed or duplicate cases.
- **CP2:** Separate a judge's schema-validated verdict from its explanation.
  Evidence: a replay command checks one verdict per source case.
- **CP3:** Turn gold labels and judge verdicts into TP, FP, FN, TN, precision,
  and recall. Evidence: the capstone prints all six values deterministically.

## Backwards lesson plan

### Lesson 1: Make a small eval set comparable

Checkpoint: CP1. The build creates `cases.jsonl`, a labeled fixture that later
lessons treat as the source of truth.

### Lesson 2: Replay an LLM judge with a contract

Checkpoint: CP2. The build consumes the Lesson 1 fixture and emits one validated
cached judgment per case. It models the boundary where a live structured-output
call would be cached for offline review.

### Lesson 3: Calibrate the judge instead of trusting it

Checkpoint: CP3. The build consumes the prior fixture and judgment artifact,
computes the confusion matrix, and prints precision and recall.
