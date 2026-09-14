# Evals and LLM-as-Judge: A Grader You Can Trust

This course is for an engineer who has already shipped an AI feature and needs an answer to a more useful question than "did the last demo look good?" In about 90 minutes, you will create a small, reproducible evaluation harness and use it to measure an offline replay of an LLM judge. The capstone prints a confusion matrix, precision, and recall against human labels.

## Breaking points

### BP1: A plausible example is mistaken for an evaluation set.

**Misconception:** A few hand-picked prompts can represent production quality.

**Consequence:** Regressions hide in failure modes that were not written down, and runs cannot be compared fairly.

### BP2: Judge output is treated as self-validating despite an unstable contract.

**Misconception:** A confident explanation automatically provides a usable machine-readable verdict.

**Consequence:** Missing fields and changed label meanings silently break downstream metrics.

### BP3: Agreement is reported without identifying the direction of mistakes.

**Misconception:** A single accuracy number explains whether a judge is safe for production.

**Consequence:** A judge can approve bad answers or reject useful answers while appearing acceptable.

## Checkpoints

- **CP1:** Define a compact evaluation case with a human gold label, a rubric, and a stable ID.
  Evidence: A validator rejects malformed or duplicate cases.
- **CP2:** Separate a judge schema-validated verdict from its explanation and diagnostic context.
  Evidence: A replay command checks one verdict per source case.
- **CP3:** Turn gold labels and judge verdicts into TP, FP, FN, TN, precision, and recall.
  Evidence: The capstone prints all six values deterministically.

## Pacing and artifact flow

Each lesson is **30 minutes**: four focused prose sections of **3 minutes each**
(12 minutes total), followed by one **18-minute build-along**. The three builds
remain cumulative: each creates the checked artifact consumed by the next lesson
and preserves the final offline grader capstone.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 140" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Course artifact data flow</title>
  <desc id="flow-desc">Human-labeled cases flow to a validated judge replay, then both flow to the calibrated grader.</desc>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8Z" fill="#334155"/></marker></defs>
  <rect x="12" y="38" width="190" height="64" rx="8" fill="#e0f2fe" stroke="#0369a1"/><text x="107" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0c4a6e">Lesson 1</text><text x="107" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#0c4a6e">cases.jsonl + gold labels</text>
  <path d="M202,70 H266" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="270" y="38" width="180" height="64" rx="8" fill="#fef3c7" stroke="#b45309"/><text x="360" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#78350f">Lesson 2</text><text x="360" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#78350f">judgments.jsonl</text>
  <path d="M450,70 H514" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="518" y="38" width="190" height="64" rx="8" fill="#dcfce7" stroke="#15803d"/><text x="613" y="64" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#14532d">Lesson 3 capstone</text><text x="613" y="86" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#14532d">matrix, precision, recall</text>
</svg>

## Backwards lesson plan

### Lesson 1: Make a small eval set comparable

Checkpoint: CP1. The build creates `cases.jsonl`, a labeled fixture that later lessons treat as the source of truth.

Pacing: 3 min x 4 prose sections, then an 18-minute build (30 minutes total).

### Lesson 2: Replay an LLM judge with a contract

Checkpoint: CP2. The build consumes the Lesson 1 fixture and emits one validated cached judgment per case. It models the boundary where a live structured-output call would be cached for offline review.

Pacing: 3 min x 4 prose sections, then an 18-minute build (30 minutes total).

### Lesson 3: Calibrate the judge instead of trusting it

Checkpoint: CP3. The build consumes the prior fixture and judgment artifact, computes the confusion matrix, and prints precision and recall.

Pacing: 3 min x 4 prose sections, then an 18-minute build (30 minutes total).
