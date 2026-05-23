"""Phase 4 engine result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from zm.models import RecommendationDisplay, RecommendationResult

EngineSource = Literal["groq", "fallback"]


@dataclass(frozen=True)
class EngineResult:
    """Output after Groq ranking (or fallback)."""

    result: RecommendationResult
    displays: list[RecommendationDisplay]
    source: EngineSource
    warning: str | None = None
