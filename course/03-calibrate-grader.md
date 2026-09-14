# Lesson 3: Calibrate the Judge Instead of Trusting It

Checkpoints: CP3

**Pacing:** Four 3-minute prose sections (12 minutes), then an 18-minute
build-along (30 minutes total).

## Section 1 — 3 minutes: A confusion matrix keeps mistakes directional

The final question is not "how many times did the judge agree?" It is "which
decisions does the judge get wrong, and what will that cost the product?" A
confusion matrix answers this by crossing the human reference label with the
judge's prediction. For a positive class of `pass`, true positives are answers
both human and judge approve. True negatives are answers both reject. False
positives are answers the judge approves even though the human label says fail.
False negatives are answers the judge rejects even though the human label says
pass.

The positive class is a design choice, so state it. Here, a positive prediction
means "this answer can pass." That makes a false positive particularly
interesting: an unsafe or unhelpful answer may be allowed through. A false
negative means useful work is sent for unnecessary review or discarded. Another
product might define positive as "needs escalation"; its precision and recall
would describe that different action. Metrics are not portable labels pasted on
top of arbitrary decisions.

The grader joins each Lesson 2 judgment with a Lesson 1 human label using
`case_id`. It never trusts line order. It first checks that the ID sets match,
then increments exactly one matrix cell for each case. The command prints the
matrix as `TP`, `FP`, `FN`, and `TN`, followed by the IDs in each error group.
Those IDs matter more than the rounded rate. A rate tells you whether to look;
the cases tell you what to change.
Those labels make the metric report actionable during prompt reviews and release
decisions.

This fixture produces three true positives, three true negatives, one false
positive, and one false negative. You can verify the arithmetic manually:
eight source cases equal the sum of the four cells. If the total does not
match, stop. A metric calculated after a partial join is not conservative; it
is wrong. The visible accounting check turns a subtle data mismatch into an
immediate failure.

## Section 2 — 3 minutes: Precision and recall name different product risks

Precision asks: among the answers the judge approved, how many were actually
passing according to the human label? Its formula is `TP / (TP + FP)`. In the
fixture, precision is `3 / (3 + 1) = 0.750`. The false positive lowers
precision because it represents an approval that should not have happened. If
the judge gates customer-facing content, precision is often the safety-oriented
metric: low precision means a green light is not trustworthy.

Recall asks: among the answers the human label says should pass, how many did
the judge approve? Its formula is `TP / (TP + FN)`. Here recall is also
`3 / (3 + 1) = 0.750`. The false negative lowers recall because the judge missed
a valid answer. If the judge routes candidates into an automatic publish path,
low recall may cause needless manual work and slow the product down.

Neither rate tells you which threshold is correct by itself. A stricter judge
can improve precision by rejecting more answers while damaging recall. A more
permissive judge can improve recall while letting unsafe answers through. Choose
the trade-off from the downstream action and measure it on data that resembles
the traffic that action will see. For high-risk policy claims, you may require
high precision and accept a human-review queue. For a low-risk drafting tool,
you may optimize recall and audit a sample of approvals.

The grader protects against a zero denominator. If no answer is predicted to
pass, precision is undefined; printing `0.000` would falsely imply knowledge.
The code prints `n/a` instead. The same applies when the reference set contains
no actual passes. In a real report, class counts should sit beside every rate so
readers can see whether a seemingly perfect score came from two examples or two
thousand.
Always preserve those denominators and class definitions in reports, alerts,
and release notes.

## Section 3 — 3 minutes: Calibration is an iteration loop, not a score hunt

A first confusion matrix is a diagnosis, not a release decision. Start with
the false positives because they show where the judge's approval criterion is
too loose. Read the human rubric, the candidate answer, and the judge reason
together. In this fixture, the judge accepts an invented "30-day" exception.
The next prompt version should explicitly reject unsupported exceptions and the
next eval set should include more variants of that failure mode. Do not simply
edit this single cached verdict: that would make the score better without
making the judge better.

Then inspect false negatives. The fixture's judge rejects a valid paraphrase of
the seven-day policy. That may signal a rubric that rewards exact wording more
than policy fidelity. Test a revised judge instruction against a held-out case
where the wording differs but the policy remains correct. If the revised
instruction also starts approving invented policy, the trade-off is visible in
precision and recall rather than hidden in a prompt anecdote.

Keep three versions separate: the dataset version, the rubric or prompt version,
and the judge model version. A changed score is uninterpretable when all three
changed at once. Cache structured verdicts for each run, preserve the exact
source IDs, and record the metrics with their counts. As the set grows, slice
the matrix by language, request type, customer tier, or known failure mode; an
overall score can conceal a serious regression in a small but important slice.

You now hold a working grader, not an LLM demo. It replays without an API call,
fails on incomplete artifacts, and prints a confusion matrix with precision and
recall. Its sample is intentionally tiny, so it cannot certify production
quality. It can, however, make the next model or prompt change argue with
evidence instead of confidence.
That discipline makes later metric changes explainable instead of merely
impressive-looking numbers on a release dashboard.

## Section 4 — 3 minutes: A metric needs a decision rule

Precision and recall become useful only when someone decides what happens at a
given result. A dashboard that reports `0.750` without an intended action
invites score watching rather than calibration. Start with the product
consequence: is a predicted pass automatically shown to a customer, routed to
a human reviewer, or used only to rank work? The consequence determines which
error deserves a tighter limit. It also determines whether this small fixture
is a diagnostic signal or enough evidence for a release decision.

For the support-policy example, approving an invented exception is more costly
than sending a sound answer to review. A reasonable initial rule might be:
do not auto-approve until precision exceeds an agreed safety target on a
representative, independently held-out set; send uncertain or failing cases to
review in the meantime. That rule does not make 0.750 inherently bad. It makes
the next action explicit: inspect the single false positive, improve the
rubric or prompt, and test the revision without changing the ruler midstream.

Thresholds belong to the decision process, not to the formula. This exercise's
judge emits a boolean prediction, so the build exposes a fixed pass boundary.
Many production judges instead produce a score or a structured severity label.
For those systems, evaluate several candidate thresholds against the same
held-out labels and report the resulting matrix at each one. Choose a
threshold before looking at the final holdout whenever possible; otherwise the
team can accidentally select the one that best fits noise. Preserve the chosen
threshold with the prompt and model version.

Counts constrain confident stories. Four approvals with one false positive
produce 0.750 precision, but they do not prove the next four approvals will
behave the same way. Keep the numerator and denominator next to every rate,
and add uncertainty estimates as the dataset becomes large enough to support
them. Until then, use the matrix as a map of known behavior. It is valuable
because it directs investigation to concrete cases, not because it supplies a
universal quality certificate.

The capstone’s result should therefore lead to a written decision: retain the
current offline judge as a baseline, revise the handling of the observed
failure modes, or collect more labels before changing automation. That closes
the loop between a classifier metric and product risk. Calibration is complete
only when the measured trade-off changes what the team will test, ship, or
review next.

## Build-along

The capstone consumes `cases.jsonl` from Lesson 1 and the normalized `judgments.jsonl` generated in Lesson 2. Run the Lesson 2 command first if the judgment artifact is absent.

Continue in `build/lesson_03_calibrate-grader/BUILD.md`.

Artifact contract for the next lesson: `output/lesson-03-expected.txt`
