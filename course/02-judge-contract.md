# Lesson 2: Replay an LLM Judge with a Contract

Checkpoints: CP2

**Pacing:** Four 3-minute prose sections (12 minutes), then an 18-minute
build-along (30 minutes total).

## Section 1 — 3 minutes: A judge has two outputs with different jobs

An LLM-as-judge is a model call that evaluates a candidate output against a
rubric. The useful output is not a paragraph saying "looks good." It is a
small, typed decision that downstream code can trust enough to measure. In this
course, the judgment contract has three fields: the source `case_id`, a boolean
`predicted_pass`, and a short `reason`. The boolean is for metrics; the reason
is for diagnosis. Mixing their jobs is a common source of fragile pipelines.

Suppose a model returns, "Mostly correct, but I would mention the order number."
A human can infer a verdict, but code cannot safely decide whether "mostly
correct" means pass. If you derive the boolean by searching the prose for words
such as "pass," then prompt wording becomes an undocumented API. Instead, ask
the model for structured output with a JSON Schema or a provider's structured
output feature. Validate the returned object again at your application boundary.
Provider guarantees reduce malformed responses; they do not verify that the
response belongs to the correct case or that all expected cases were judged.

The build replays cached judgments instead of calling a paid API. That is a
feature, not a watered-down simulation. A live system should cache the exact
structured result, plus the prompt version and model identifier, before
computing a dashboard. Offline replay lets a reviewer reproduce the calibration
without credentials and lets an engineer separate "the model changed" from "the
metric code changed." The cached file here is intentionally readable JSONL so
you can inspect every verdict and reason.

The source fixture remains the owner of the human label. The judgment artifact
does not copy `expected_pass`; it only names a source ID and gives the judge's
prediction. Duplicating ground truth into the judge file creates two sources of
truth that can silently diverge. Lesson 3 will join the two artifacts by ID and
fail fast if either side has missing or extra cases.

## Section 2 — 3 minutes: Validation is a product boundary, not an afterthought

JSON parsing is not validation. A line can be valid JSON and still be unusable:
an array instead of an object, a string where a boolean is required, an unknown
case ID, a duplicate verdict, or a reason that has been replaced with `null`.
Each of these errors has a different operational meaning. Treating them all as
"the model was weird" makes the next incident needlessly hard to investigate.

The replay command in the build performs four checks before it writes
`judgments.jsonl`. It verifies the exact key set and value types for each
cached line, confirms that every `case_id` exists in the Lesson 1 fixture,
rejects duplicate IDs, and compares the final set of IDs to the source set.
Set equality is important. A count alone cannot distinguish "eight unique
judgments" from "seven expected judgments plus one judgment for an old case."
The command prints a visible `PASS` line only after all checks succeed.
It also lets an incident reviewer compare two judge runs without reconstructing
their order.

This is the same shape as a live boundary. In a production implementation, the
input to this validator would be a response parsed using Pydantic, Zod, or a
JSON Schema. You would additionally record the rubric version, prompt template
version, model snapshot, temperature, and timestamp. Do not use a volatile
alias such as `latest` without recording the resolved model ID; otherwise an
identical replay command may evaluate a different judge tomorrow.

Do not repair a bad verdict by coercion. Converting `"true"` to `true`, filling
in an omitted `case_id` from line order, or accepting extra fields because they
"probably do not matter" hides a contract break. Fail with the line number and
case ID. A broken evaluation is better than a believable metric computed from
unknown inputs. Once the output is valid, write the normalized lines in stable
source-fixture order. Stable order makes a diff tell you what changed.

## Section 3 — 3 minutes: A rubric controls the judge's measurement target

The judge is not an oracle; it is a classifier conditioned on its rubric. If
the rubric says "be helpful," a judge may reward invented exceptions because
they sound accommodating. If the rubric says "must quote the policy verbatim,"
it may reject a concise but accurate paraphrase. Both outcomes can be coherent
with their prompts and useless for the product. The measurement target must be
explicit before you tune the prompt.

Read the Lesson 1 rubrics as test specifications. They define a narrow desired
behavior: accurate policy, no invented promise, and a usable action. The cached
judge intentionally makes two mistakes. It rejects one valid paraphrase, which
becomes a false negative, and it accepts one confident invented exception,
which becomes a false positive. Those mistakes are not defects in the exercise.
They are evidence that metrics can distinguish over-strictness from unsafe
leniency.

When you inspect a disagreement, change one variable at a time. If the human
label was wrong under the documented policy, fix the fixture in a new version.
If the rubric is underspecified, revise the rubric and relabel affected cases.
If the rubric is sound but the judge misses it, revise the judge prompt or
route that failure mode to a stronger model. Re-running a prompt until the
score rises is not calibration; it is overfitting unless you preserve a held-out
set for the next decision.

The output of this lesson is not a quality claim. It is a validated set of
judge predictions that Lesson 3 can compare with the human reference. Because
the replay consumes Lesson 1's artifact by path and preserves its IDs, the
capstone can prove exactly which source cases produced each matrix cell.
Retain this cache as the reproducible baseline before changing a prompt,
switching the judge model, or publishing a durable comparison.

## Section 4 — 3 minutes: Provenance makes a judge run comparable

A valid judgment file is not yet a comparable experiment. The same JSON shape
can describe verdicts produced by a different rubric, a changed prompt, or a
new model snapshot. If those inputs are not named, a later precision change
cannot be attributed. The file may still be useful for debugging a single
case, but it cannot support the question the course is teaching: did this judge
become better or worse against the same human standard?

Treat the cached replay as a measurement record. At minimum, associate it with
the fixture version, rubric or prompt version, model identifier, and decoding
settings such as temperature. A production record should also include when the
run happened and a content hash of the inputs. The cache in this build stays
small on purpose: `judgments.jsonl` holds the contract that the grader consumes,
while the checked build material documents the fixed replay. That separation
prevents metadata from becoming a second copy of the human labels or from
changing the simple join Lesson 3 must demonstrate.

Stable ordering helps make the record reviewable, but it is not identity.
Write judgments in the source fixture's order so a line-by-line diff is easy
to read; still use `case_id` as the only key when validating or grading. A
reordered fixture then produces a harmless presentation change instead of a
silent relabeling. Conversely, a changed case ID or a missing ID must fail even
when the number of lines looks right. The distinction lets people review a
meaningful model change without mistaking formatting for evidence.

Version changes need deliberate comparisons. When a prompt is revised to
reject invented exceptions, save the old cache and create a new cache with the
new prompt version. Grade each against the same fixture before deciding whether
the revision is an improvement. If the fixture also changes, report that as a
new benchmark rather than comparing the two scores directly. This discipline
does not require a large platform: filenames, a manifest, and immutable source
artifacts are enough for the small exercise.

The next lesson therefore receives a verified prediction artifact with a
clear lineage. Its numbers can be traced back to particular source cases and a
specific judge configuration, rather than to a vague statement that “the
model” was tested. Reproducibility is what turns structured output from a
convenient integration format into evidence suitable for calibration.

## Build-along

The cached JSONL represents structured output captured from a judge. A live implementation would validate a provider response at this same boundary and cache the normalized records for replay.

Continue in `build/lesson_02_judge-contract/BUILD.md`.

Artifact contract for the next lesson: `build/lesson_02_judge-contract/judgments.jsonl`
