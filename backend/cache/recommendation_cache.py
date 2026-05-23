"""In-memory TTL cache for recommendation responses (Phase 6)."""

from __future__ import annotations

import hashlib
import json
import time
from threading import Lock
from typing import Any

from backend.api.schemas import RecommendationResponse

_CACHE: RecommendationCache | None = None


class RecommendationCache:
    """Thread-safe cache keyed by normalized request JSON."""

    def __init__(self, ttl_seconds: int, *, max_entries: int = 256) -> None:
        self._ttl = max(0, ttl_seconds)
        self._max_entries = max_entries
        self._store: dict[str, tuple[float, RecommendationResponse]] = {}
        self._lock = Lock()

    @property
    def enabled(self) -> bool:
        return self._ttl > 0

    def make_key(self, payload: dict[str, Any]) -> str:
        normalized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, key: str) -> RecommendationResponse | None:
        if not self.enabled:
            return None
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, response = entry
            if now >= expires_at:
                del self._store[key]
                return None
            return response

    def set(self, key: str, response: RecommendationResponse) -> None:
        if not self.enabled:
            return
        expires_at = time.monotonic() + self._ttl
        with self._lock:
            if len(self._store) >= self._max_entries:
                oldest_key = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest_key]
            self._store[key] = (expires_at, response)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


def get_recommendation_cache(ttl_seconds: int) -> RecommendationCache:
    global _CACHE
    if _CACHE is None or _CACHE._ttl != ttl_seconds:
        _CACHE = RecommendationCache(ttl_seconds)
    return _CACHE
