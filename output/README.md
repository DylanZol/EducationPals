# Captured offline output

`lesson-01-run.txt` through `lesson-03-run.txt` are the real stdout captured by
`python scripts/replay_submission.py`. The script compares each captured run
with its `lesson-0N-expected.txt` fixture and exits nonzero if any output
changes. `lesson-03-capstone-expected.txt` is the exact output expected from
the final grader command.
