"""Structured timing logs for recommendation pipeline (Phase 6)."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Iterator

from backend.middleware.request_id import request_id_ctx

logger = logging.getLogger("zm.api")


@contextmanager
def log_phase(phase: str, **extra: object) -> Iterator[None]:
    """Log duration_ms for a pipeline phase with request_id."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "phase=%s duration_ms=%s request_id=%s %s",
            phase,
            duration_ms,
            request_id_ctx.get() or "-",
            " ".join(f"{k}={v}" for k, v in extra.items()),
        )
