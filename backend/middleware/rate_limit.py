"""Simple per-IP rate limiting (Phase 6)."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window rate limiter (in-memory, single process)."""

    def __init__(self, app, *, requests_per_minute: int) -> None:
        super().__init__(app)
        self._limit = max(0, requests_per_minute)
        self._window_seconds = 60
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        if self._limit <= 0:
            return await call_next(request)

        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        now = time.monotonic()
        key = self._client_key(request)
        window_start = now - self._window_seconds
        hits = [t for t in self._hits[key] if t > window_start]
        if len(hits) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={
                    "ok": False,
                    "message": "Too many requests. Please try again shortly.",
                    "errors": {},
                },
            )
        hits.append(now)
        self._hits[key] = hits
        return await call_next(request)
