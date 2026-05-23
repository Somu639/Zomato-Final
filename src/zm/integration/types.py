"""Phase 3 result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zm.models import Restaurant, UserPreferences


@dataclass(frozen=True)
class FilterStats:
    """Counts at each filtering stage (for logging and user hints)."""

    location_count: int
    after_rating: int
    after_cuisine: int
    after_budget: int
    after_top_k: int


@dataclass(frozen=True)
class IntegrationResult:
    """Output of the integration layer ready for Phase 4 LLM."""

    preferences: UserPreferences
    candidates: list[Restaurant]
    context: dict[str, Any]
    context_json: str
    prompt_version: str
    system_prompt: str
    user_prompt: str
    filter_stats: FilterStats
    no_match_message: str | None = None

    @property
    def has_candidates(self) -> bool:
        return bool(self.candidates)
