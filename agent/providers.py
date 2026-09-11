"""Live OpenAI and exact-cache replay providers."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


class CacheError(RuntimeError):
    """Raised when an offline cache is absent, stale, or malformed."""


class CacheStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, cache_key: str) -> Path:
        if not cache_key or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in cache_key):
            raise ValueError(f"Unsafe cache key: {cache_key!r}")
        return self.root / f"{cache_key}.json"

    def save(self, cache_key: str, envelope: dict[str, object]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.path_for(cache_key)
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(destination)

    def load(self, cache_key: str) -> dict[str, object]:
        source = self.path_for(cache_key)
        if not source.exists():
            raise CacheError(
                f"Missing {source}. Run live generation once before using --offline."
            )
        value = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise CacheError(f"Cache envelope must be an object: {source}")
        return value


class CachedProvider:
    def __init__(self, cache: CacheStore) -> None:
        self.cache = cache
        self.records: list[dict[str, object]] = []

    def generate(self, cache_key: str, prompt: str, schema: type[SchemaT]) -> SchemaT:
        envelope = self.cache.load(cache_key)
        actual_hash = envelope.get("prompt_sha256")
        expected_hash = prompt_hash(prompt)
        if actual_hash != expected_hash:
            raise CacheError(
                f"Stale cache for {cache_key}: prompt hash {actual_hash!r} != {expected_hash!r}."
            )
        try:
            parsed = schema.model_validate(envelope["output"])
        except (KeyError, ValueError) as error:
            raise CacheError(f"Invalid cached output for {cache_key}: {error}") from error
        self.records.append({key: value for key, value in envelope.items() if key != "output"})
        return parsed


class OpenAIProvider:
    def __init__(self, cache: CacheStore, model: str) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for live generation.")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("Install dependencies with: python -m pip install -r requirements.txt") from error

        self.client = OpenAI()
        self.cache = cache
        self.model = model
        self.records: list[dict[str, object]] = []

    def generate(self, cache_key: str, prompt: str, schema: type[SchemaT]) -> SchemaT:
        response = self.client.responses.parse(
            model=self.model,
            input=[{"role": "user", "content": prompt}],
            text_format=schema,
            store=False,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError(f"{cache_key} returned no parsed output (status={response.status!r}).")

        usage = response.usage.model_dump(mode="json") if response.usage else None
        envelope: dict[str, object] = {
            "cache_key": cache_key,
            "created_at": datetime.now(UTC).isoformat(),
            "model": response.model,
            "prompt_sha256": prompt_hash(prompt),
            "response_id": response.id,
            "usage": usage,
            "output": parsed.model_dump(mode="json"),
        }
        self.cache.save(cache_key, envelope)
        self.records.append({key: value for key, value in envelope.items() if key != "output"})
        return parsed
