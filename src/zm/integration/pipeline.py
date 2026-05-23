"""Integration pipeline: filter, rank, package context and prompts."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from zm.config import Settings, get_settings
from zm.integration.context import build_llm_context_json
from zm.integration.filters import apply_hard_filters
from zm.integration.prompts import PROMPT_VERSION, build_prompt_payload, build_prompts
from zm.integration.scoring import rank_candidates
from zm.integration.types import FilterStats, IntegrationResult
from zm.models import Restaurant, UserPreferences

if TYPE_CHECKING:
    from zm.interfaces.data_source import RestaurantRepositoryPort

logger = logging.getLogger(__name__)


def build_no_match_message(preferences: UserPreferences, stats: FilterStats) -> str:
    """Actionable message when zero candidates remain (P3-01)."""
    parts = [
        f"No restaurants match your preferences in {preferences.location}.",
        "Try relaxing:",
    ]
    if stats.after_rating < stats.location_count:
        parts.append(f"- Lower minimum rating (currently {preferences.min_rating})")
    if stats.after_cuisine < stats.after_rating:
        parts.append(f"- Broaden cuisines (currently {', '.join(preferences.cuisines)})")
    if stats.after_budget < stats.after_cuisine:
        parts.append(f"- Change budget band (currently {preferences.budget.value})")
    if stats.location_count == 0:
        parts[0] = f"No restaurants found for {preferences.location}."
    return " ".join(parts)


def build_candidate_set(
    preferences: UserPreferences,
    restaurants: list[Restaurant],
    *,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> tuple[list[Restaurant], FilterStats, str | None]:
    """
    Filter, rank, and cap candidates.

    Returns:
        (candidates, filter_stats, no_match_message)
    """
    settings = settings or get_settings()
    top_k = top_k if top_k is not None else settings.top_k_candidates

    filtered, stats = apply_hard_filters(restaurants, preferences)
    ranked = rank_candidates(filtered, preferences)
    capped = ranked[:top_k]

    final_stats = FilterStats(
        location_count=stats.location_count,
        after_rating=stats.after_rating,
        after_cuisine=stats.after_cuisine,
        after_budget=stats.after_budget,
        after_top_k=len(capped),
    )

    if not capped:
        message = build_no_match_message(preferences, stats)
        logger.info("No candidates after filters: %s", message)
        return [], final_stats, message

    logger.info(
        "Candidates: %s -> %s after filters, returning top %s",
        stats.location_count,
        stats.after_budget,
        len(capped),
    )
    return capped, final_stats, None


def build_candidate_set_from_repo(
    preferences: UserPreferences,
    repository: RestaurantRepositoryPort,
    *,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> tuple[list[Restaurant], FilterStats, str | None]:
    """Load location slice from repository, then filter and rank."""
    location_restaurants = repository.filter_by_location(preferences.location)
    return build_candidate_set(
        preferences,
        location_restaurants,
        top_k=top_k,
        settings=settings,
    )


def run_integration(
    preferences: UserPreferences,
    repository: RestaurantRepositoryPort,
    *,
    settings: Settings | None = None,
) -> IntegrationResult:
    """
    Full Phase 3 pipeline: candidates, context JSON, and prompt v1.

    Does not call the LLM (Phase 4).
    """
    settings = settings or get_settings()
    candidates, stats, no_match = build_candidate_set_from_repo(
        preferences,
        repository,
        settings=settings,
    )

    if not candidates:
        empty_context, empty_json = build_llm_context_json([], preferences)
        system_prompt, user_prompt = build_prompts(
            preferences,
            empty_json,
            display_top_n=settings.display_top_n,
        )
        return IntegrationResult(
            preferences=preferences,
            candidates=[],
            context=empty_context,
            context_json=empty_json,
            prompt_version=PROMPT_VERSION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            filter_stats=stats,
            no_match_message=no_match,
        )

    context, context_json = build_llm_context_json(candidates, preferences)
    system_prompt, user_prompt = build_prompts(
        preferences,
        context_json,
        display_top_n=settings.display_top_n,
    )
    build_prompt_payload(
        preferences,
        context,
        context_json,
        display_top_n=settings.display_top_n,
    )

    return IntegrationResult(
        preferences=preferences,
        candidates=candidates,
        context=context,
        context_json=context_json,
        prompt_version=PROMPT_VERSION,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        filter_stats=stats,
        no_match_message=no_match,
    )
