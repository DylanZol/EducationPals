# Cached model responses

Each successful live call writes a sanitized JSON envelope here. Envelopes hold
the parsed structured output, model name, prompt hash, token usage, and response
ID. They never contain the API key.

Commit the populated cache with the final submission. `--offline` replays these
files and performs no network calls.
