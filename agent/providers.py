"""Live OpenAI and exact-cache replay providers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)
SENSITIVE_FIELD_NAMES = {
    "api_key",
    "apikey",
    "authorization",
    "password",
    "secret",
    "access_token",
    "refresh_token",
}
LIKELY_SECRET = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,}|"
    r"AIza[A-Za-z0-9_-]{16,}|OPENAI_API_KEY\s*=\s*\S+)"
)


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def canonical_json_hash(value: object) -> str:
    """Hash JSON values independently of whitespace or object key ordering."""
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def schema_name(schema: type[BaseModel]) -> str:
    return f"{schema.__module__}.{schema.__qualname__}"


class CacheError(RuntimeError):
    """Raised when an offline cache is absent, stale, or malformed."""


def _contains_secret(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() in SENSITIVE_FIELD_NAMES or _contains_secret(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    return isinstance(value, str) and LIKELY_SECRET.search(value) is not None


class CacheStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, cache_key: str) -> Path:
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
        if not cache_key or any(ch not in allowed for ch in cache_key):
            raise ValueError(f"Unsafe cache key: {cache_key!r}")
        return self.root / f"{cache_key}.json"

    def save(self, cache_key: str, envelope: dict[str, object]) -> None:
        if _contains_secret(envelope):
            raise CacheError(
                "Refusing to cache a likely credential or sensitive credential field."
            )
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.path_for(cache_key)
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(envelope, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)

    def load(self, cache_key: str) -> dict[str, object]:
        source = self.path_for(cache_key)
        if not source.exists():
            raise CacheError(
                f"Missing {source}. Run live generation once before using --offline."
            )
        try:
            value = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise CacheError(f"Invalid JSON cache envelope: {source}") from error
        if not isinstance(value, dict):
            raise CacheError(f"Cache envelope must be an object: {source}")
        if _contains_secret(value):
            raise CacheError(f"Cache envelope contains a likely credential: {source}")
        return value


class CachedProvider:
    def __init__(self, cache: CacheStore, *, require_complete: bool = False) -> None:
        self.cache = cache
        self.require_complete = require_complete
        self.records: list[dict[str, object]] = []

    def generate(self, cache_key: str, prompt: str, schema: type[SchemaT]) -> SchemaT:
        envelope = self.cache.load(cache_key)
        if self.require_complete:
            issues = validate_cache_envelope(
                envelope,
                cache_key=cache_key,
                prompt=prompt,
                schema=schema,
            )
            if issues:
                raise CacheError("\n".join(issues))
        cached_key = envelope.get("cache_key")
        if cached_key is not None and cached_key != cache_key:
            raise CacheError(f"Cache key mismatch: {cached_key!r} != {cache_key!r}.")
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
        cached_schema = envelope.get("schema")
        if cached_schema is not None and cached_schema != schema_name(schema):
            raise CacheError(
                f"Cache schema mismatch for {cache_key}: "
                f"{cached_schema!r} != {schema_name(schema)!r}."
            )
        actual_output_hash = envelope.get("output_sha256")
        expected_output_hash = canonical_json_hash(parsed.model_dump(mode="json"))
        if actual_output_hash is not None and actual_output_hash != expected_output_hash:
            raise CacheError(f"Cached output hash mismatch for {cache_key}.")
        self.records.append(cache_record(envelope))
        return parsed


class OpenAIProvider:
    def __init__(self, cache: CacheStore, model: str) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for live generation.")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError(
                "Install dependencies with: python -m pip install -r requirements.txt"
            ) from error

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
            raise RuntimeError(
                f"{cache_key} returned no parsed output (status={response.status!r})."
            )

        usage = response.usage.model_dump(mode="json") if response.usage else None
        envelope: dict[str, object] = {
            "cache_schema_version": 2,
            "cache_key": cache_key,
            "created_at": datetime.now(UTC).isoformat(),
            "model": response.model,
            "prompt_sha256": prompt_hash(prompt),
            "output_sha256": canonical_json_hash(parsed.model_dump(mode="json")),
            "schema": schema_name(schema),
            "response_id": response.id,
            "usage": usage,
            "output": parsed.model_dump(mode="json"),
        }
        self.cache.save(cache_key, envelope)
        self.records.append(cache_record(envelope))
        return parsed


def cache_record(envelope: dict[str, object]) -> dict[str, object]:
    """Return audit metadata only; prompts, outputs, and secrets never enter manifests."""
    keys = (
        "cache_schema_version",
        "cache_key",
        "created_at",
        "model",
        "prompt_sha256",
        "output_sha256",
        "schema",
        "response_id",
        "usage",
    )
    return {key: envelope[key] for key in keys if key in envelope}


def validate_cache_envelope(
    envelope: dict[str, object],
    *,
    cache_key: str,
    prompt: str,
    schema: type[SchemaT],
) -> list[str]:
    """Validate the complete replay contract used by repository verification."""
    required = {
        "cache_schema_version",
        "cache_key",
        "created_at",
        "model",
        "prompt_sha256",
        "output_sha256",
        "schema",
        "response_id",
        "usage",
        "output",
    }
    missing = required - set(envelope)
    issues = [f"{cache_key}: missing cache fields {sorted(missing)}."] if missing else []
    if set(envelope) - required:
        issues.append(
            f"{cache_key}: unsupported cache fields {sorted(set(envelope) - required)}."
        )
    if envelope.get("cache_schema_version") != 2:
        issues.append(f"{cache_key}: cache_schema_version must be 2.")
    if envelope.get("cache_key") != cache_key:
        issues.append(f"{cache_key}: cache_key does not match filename.")
    if envelope.get("prompt_sha256") != prompt_hash(prompt):
        issues.append(f"{cache_key}: prompt hash does not match the current prompt.")
    if envelope.get("schema") != schema_name(schema):
        issues.append(f"{cache_key}: schema does not match this generation stage.")
    if not isinstance(envelope.get("model"), str) or not str(envelope.get("model")).strip():
        issues.append(f"{cache_key}: model must be a non-empty string.")
    if not isinstance(envelope.get("response_id"), str) or not str(
        envelope.get("response_id")
    ).strip():
        issues.append(f"{cache_key}: response_id must be a non-empty string.")
    if envelope.get("usage") is not None and not isinstance(envelope.get("usage"), dict):
        issues.append(f"{cache_key}: usage must be an object or null.")
    try:
        datetime.fromisoformat(str(envelope.get("created_at")).replace("Z", "+00:00"))
    except ValueError:
        issues.append(f"{cache_key}: created_at must be an ISO-8601 timestamp.")
    try:
        parsed = schema.model_validate(envelope["output"])
        if envelope.get("output_sha256") != canonical_json_hash(
            parsed.model_dump(mode="json")
        ):
            issues.append(f"{cache_key}: output hash does not match schema-normalized output.")
    except (KeyError, ValueError) as error:
        issues.append(f"{cache_key}: output is invalid for {schema_name(schema)}: {error}.")
    return issues
