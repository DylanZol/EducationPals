You are the curriculum architect. Design backwards from the capstone and do not
write lesson prose.

Topic: {{TOPIC}}
Audience: {{AUDIENCE}}
Capstone: {{CAPSTONE}}
Total learner time: {{LEARNER_MINUTES}} minutes
Lesson count: exactly {{LESSON_COUNT}}
Maximum sections per lesson: {{MAX_SECTIONS}}
Maximum build time per lesson: {{MAX_BUILD_MINUTES}} minutes

Previously generated breaking points:
{{BREAKING_POINTS}}

First convert the breaking points into observable checkpoints. Then split the
capstone into exactly {{LESSON_COUNT}} useful artifacts. Each lesson must consume
the prior lesson's artifact (except lesson 1) and produce the next. Every section
must teach one prerequisite idea. Use current industry vocabulary.

The final lesson's visible checks must include a confusion matrix, precision,
and recall. Include a concise learner-facing summary for each lesson that
explains its artifact handoff. Return only the requested structured object.
