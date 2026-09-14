# Offline build-alongs

Each lesson folder contains four incremental commands that can be run from the
repository root without credentials or a network connection. The handoff chain
is `cases.jsonl` (Lesson 1) → `judgments.jsonl` (Lesson 2) → the calibration
report (Lesson 3).

Run `python scripts/replay_submission.py` to execute every learner command and
compare its captured output with the checked-in fixtures.
