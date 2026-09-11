from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent.providers import CacheError, CacheStore, CachedProvider, prompt_hash
from agent.schemas import ReviewResult


class CacheReplayTests(unittest.TestCase):
    def test_cache_replay_validates_prompt_hash_and_schema(self) -> None:
        prompt = "review this lesson"
        with tempfile.TemporaryDirectory() as temporary:
            cache = CacheStore(Path(temporary))
            cache.save(
                "review-01",
                {
                    "cache_key": "review-01",
                    "prompt_sha256": prompt_hash(prompt),
                    "output": {
                        "passed": True,
                        "blocking_issues": [],
                        "non_blocking_notes": ["Keep the fixture small."],
                    },
                },
            )
            result = CachedProvider(cache).generate("review-01", prompt, ReviewResult)
        self.assertTrue(result.passed)

    def test_cache_replay_rejects_stale_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cache = CacheStore(Path(temporary))
            cache.save(
                "review-01",
                {
                    "prompt_sha256": prompt_hash("old prompt"),
                    "output": {
                        "passed": True,
                        "blocking_issues": [],
                        "non_blocking_notes": [],
                    },
                },
            )
            with self.assertRaises(CacheError):
                CachedProvider(cache).generate("review-01", "new prompt", ReviewResult)


if __name__ == "__main__":
    unittest.main()
