# Cached model responses

Each successful live call writes a sanitized schema-version-2 JSON envelope
here. An envelope records its cache key, timestamp, model, response ID, prompt
SHA-256, schema name, schema-normalized output SHA-256, optional usage, and the
parsed structured output. Prompts and API keys are never stored.

Commit every stage: foundations, each lesson attempt, and each review. Offline
replay validates the current prompt hash, output hash, and Pydantic schema
before rendering; `verify` rejects incomplete envelopes, stale hashes, missing
stages, and manifests that do not precisely record the replay calls. `--offline`
performs no network calls.
