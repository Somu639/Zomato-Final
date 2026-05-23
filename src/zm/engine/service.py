"""End-to-end recommend: validate → integrate → Groq."""

from __future__ import annotations

from typing import TYPE_CHECKING

from zm.config import Settings, get_settings
from zm.engine.pipeline import run_recommendation
from zm.engine.types import EngineResult
from zm.integration import run_integration
from zm.models import UserPreferences

if TYPE_CHECKING:
    from zm.interfaces.data_source import RestaurantRepositoryPort


def recommend(
    preferences: UserPreferences,
    repository: RestaurantRepositoryPort,
    *,
    settings: Settings | None = None,
) -> EngineResult:
    """Run Phase 3 integration then Phase 4 Groq ranking."""
    settings = settings or get_settings()
    integration = run_integration(preferences, repository, settings=settings)
    if not integration.has_candidates:
        raise ValueError(integration.no_match_message or "No matching restaurants")
    return run_recommendation(integration, repository, settings=settings)
