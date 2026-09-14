# Submission writeup

## What I cut and why

I cut prompt optimization, judge ensembles, inter-rater reliability, confidence
calibration, ROC curves, and production sampling infrastructure. They are
important, but each requires a decision about the measurement target that a
90-minute first course cannot responsibly hide. I also cut a live API call from
the learner build. A live call would make the exercise less reproducible,
require a paid credential, and encourage attention on provider syntax instead
of the data and metric contracts. The build uses cached structured judgments to
make the same boundary visible offline.

I kept a small binary fixture because the capstone needs an inspectable
confusion matrix. The course does not claim that eight cases represent
production traffic. Instead, it teaches why a compact diagnostic slice needs
stable IDs, a rubric, human labels, schema validation, and a join before it can
support a calibration discussion. Three short artifacts compound: source
fixture, validated judgment replay, then grader. That path leaves out useful
advanced material, but it means every concept directly changes a command the
learner can run and inspect.

## Where the course is weakest

The weakest part is the bridge from this deliberately balanced, tiny diagnostic
fixture to a production evaluation set. The examples make the confusion matrix
easy to verify by hand, but they do not teach sampling from real traffic,
handling ambiguous labels, or reporting uncertainty. A learner could overread
the printed 0.750 precision and recall as a statement about a deployed system
rather than a statement about eight known cases. The lessons say that the
fixture is not representative, but the build cannot demonstrate the difference
without adding collection and annotation work that would break the time budget.

In another iteration, I would add a second, read-only fixture drawn from a
different request type and ask the grader to print per-slice counts beside the
overall matrix. I would also add two independently labeled boundary cases and
show how a disagreement changes the dataset rather than being forced into a
boolean. Those additions would make distribution shift and label policy more
concrete, though I would preserve the current offline cache and strict joins.
