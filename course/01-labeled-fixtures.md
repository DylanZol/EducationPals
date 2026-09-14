# Lesson 1: Make a Small Eval Set Comparable

Checkpoints: CP1

**Pacing:** Four 3-minute prose sections (12 minutes), then an 18-minute
build-along (30 minutes total).

## Section 1 — 3 minutes: An eval case is a decision, not a prompt collection

An evaluation set is useful when it lets you make the same product decision on
two different versions of a system. That requirement sounds modest, but it
rules out most ad hoc prompt lists. A prompt by itself has no statement of what
good looks like. A model answer by itself has no stable reason to pass or fail.
When the next model version behaves differently, a teammate can always explain
away the difference: perhaps the new answer is more creative, perhaps the
reviewer was stricter, perhaps the prompt was unusual. Those explanations may
be true, but they do not make a regression measurable.

Start with a narrow unit of behavior. In this course, the behavior is whether a
support assistant's answer is safe and useful for a refund request. Each case
has an `id`, the user `prompt`, a candidate `answer`, a short `rubric`, and a
human `expected_pass` label. The label is deliberately binary, not because all
quality is binary, but because a binary contract makes the first calibration
visible. A passing answer must answer the request without inventing a policy; a
failing answer either gives a wrong policy or evades a request that the rubric
says should be answered.

The candidate answer belongs in the fixture. If a run generates fresh answers
while you evaluate, you have changed both the system under test and the test
input. That is appropriate for a generation benchmark, but it is a poor first
tool for debugging a judge. Freezing answers makes the question precise:
"given these known examples, how often does this judge agree with the human
decision?" A stable ID makes it possible to join verdicts back to cases without
depending on their order. The rubric makes a disagreement inspectable rather
than mystical. Keep the fixture small enough to read in one sitting. Eight
diverse cases reveal more than eighty near duplicates.

This is not a statistically representative production sample. It is a
diagnostic slice. Include obvious passes and obvious failures, then include the
boundary cases that cause real arguments: a correct answer with awkward wording,
a polite non-answer, a confident invented rule, and an answer that gives a
correct policy but misses a required condition. Later, sample production data
and stratify it by traffic and failure mode. First, create a fixture whose
meaning another engineer can audit.

## Section 2 — 3 minutes: Labels need a policy before they need a spreadsheet

Human labels are the reference point for the calibration in Lesson 3, so an
ambiguous label is not harmless setup work. A label answers a specific question
under a specific rubric. It does not answer whether you personally liked the
answer, whether the tone was charming, or whether a different product might
allow it. Write the decision rule in the case and apply it consistently. If a
case genuinely has two reasonable outcomes, record that uncertainty and remove
it from a binary starter set rather than pretending the label is objective.

The simplest label policy is an inclusion test. For a refund assistant, a pass
must state the seven-day policy accurately when that policy is relevant, must
not promise an exception without evidence, and must give a usable next action.
That policy produces a useful distinction. "Refunds are allowed within seven
days; reply with your order number" passes. "We always refund anything,
including purchases from years ago" fails even though it sounds helpful.
"Contact support" may fail when the prompt asks for the documented policy,
because it withholds an answer the assistant should provide.

Avoid balancing labels by editing reality. A 50/50 fixture is convenient for
learning a confusion matrix, but real production rates may be very different.
What matters now is coverage of known risks. State why a case exists in the
rubric, use the same policy for all cases, and make labels booleans rather than
strings such as `"good"` and `"bad"`. Boolean values prevent accidental
truthiness bugs and give the metric code one explicit type to compare.

The build's validator enforces mechanics: every JSON line must be an object,
IDs must be unique, all required fields must exist, and at least one passing and
one failing case must be present. It cannot prove that the labels are wise.
That is the human responsibility. The visible check is still valuable because
bad mechanics otherwise become confusing model failures in the next lesson.
Once it passes, commit the fixture. Treat later changes as versioned data, not
as invisible edits to the ruler used to measure model quality.

## Section 3 — 3 minutes: Baselines make later disagreement informative

Before invoking an LLM judge, run a deliberately simple baseline over the
fixture. This course's baseline does not try to be clever: it only verifies
that the fixture can be parsed and reports the number of human pass and fail
labels. That may look trivial, but it establishes two habits that prevent
expensive debugging. First, the data contract is exercised before a model is
introduced. Second, every later command has a visible, deterministic output
that can be compared with the checked-in `output/` files.

In a production evaluation, a baseline might be a rule, a previous model, or a
human-review sample. The point is not that rules outperform models. The point
is that a model score without a reference is difficult to interpret. If a new
judge says every answer passes, its raw agreement may still look high when
almost all production answers are good. A label-count baseline reminds you of
the class balance, while the capstone's false-positive and false-negative
counts show the direction of the problem.

Run commands from the repository root. The code locates its fixture relative to
its own file, so it does not depend on your current working directory. Read the
printed case IDs when the validator fails; do not repair data by deleting lines
until it becomes green. A duplicate ID is a join error waiting to happen. A
missing rubric is a future disagreement that cannot be resolved. A string label
is a type contract that has already drifted.

At the end of this lesson, `cases.jsonl` is the artifact contract for Lesson 2.
It contains the frozen candidate answers and the human labels, while the
baseline proves it is well formed. Lesson 2 will consume that exact file, add
an offline replay of judge verdicts, and preserve the source IDs. Nothing is
being scored yet. That separation is intentional: first build a ruler, then
check whether the judge reads it consistently.

## Section 4 — 3 minutes: Coverage makes a small fixture useful

Fixture size is a budget, not a proxy for rigor. A small set earns its place
when every case probes a decision that could otherwise hide behind an average.
Start by naming the ways the assistant can fail: inventing a policy, omitting a
condition, declining a request it should answer, or following the policy with
an unusable next step. Then choose one or two cases for each failure mode. That
method gives the eight examples a purpose beyond variety. It also makes the
next addition obvious when a production incident exposes a new mistake.

Coverage is different from random sampling. A random sample can estimate the
frequency of common behavior, but it may contain no examples of a rare,
high-cost policy claim. A diagnostic fixture deliberately overrepresents
boundary cases because its job is to reveal whether a change handles them. For
example, include both an answer that says refunds are allowed within seven days
and an accurate paraphrase that says customers have one week. The pair tests
whether a later judge measures policy fidelity or merely rewards a copied
phrase. Include an invented thirty-day exception as a separate failure, because
its confidence is part of the risk.

Do not turn coverage into a hidden scoring trick. If four cases all express the
same invented exception with minor punctuation changes, a judge that learns
that phrase receives too much credit. Prefer cases that vary the wording,
request shape, and reason for the decision while preserving the documented
rule. Give each case a stable ID that hints at its role, such as
`valid-paraphrase` or `invented-exception`; the ID is an audit handle, not
evidence for the model. Keep the rubric sufficient for a reviewer to explain
the label without consulting unwritten assumptions.

After the first run, use disagreements to prioritize coverage rather than to
inflate the score. A false positive involving a policy exception suggests a new
variant for a future fixture version; it does not justify relabeling the
existing case. Preserve the original set as the comparison ruler, and add
cases with a recorded reason. This course's fixture is intentionally a
diagnostic slice, not a production estimate. Its disciplined coverage gives
Lesson 2 a meaningful, inspectable input while keeping the build short enough
to complete in one session.

## Build-along

This lesson creates the source artifact for the course. The fixture is checked in so you can focus on inspecting the contract before changing data.

Continue in `build/lesson_01_labeled-fixtures/BUILD.md`.

Artifact contract for the next lesson: `build/lesson_01_labeled-fixtures/cases.jsonl`
