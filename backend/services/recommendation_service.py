"""Orchestration service calling zm core (Phase 5a / 6)."""

from __future__ import annotations

from zm.config import Settings, get_settings
from zm.engine.pipeline import run_recommendation
from zm.engine.types import EngineResult
from zm.input.validator import validate_json
from zm.integration import run_integration
from zm.integration.context import build_llm_context_json
from zm.integration.pipeline import build_candidate_set
from zm.integration.prompts import PROMPT_VERSION, build_prompts
from zm.integration.types import FilterStats, IntegrationResult
from zm.interfaces.data_source import RestaurantRepositoryPort
from zm.models import Restaurant, UserPreferences

from backend.api.schemas import (
    FilterStatsDTO,
    PreferencesDTO,
    RecommendationItemDTO,
    RecommendationRequest,
    RecommendationResponse,
)
from backend.observability import log_phase


class NoMatchError(Exception):
    """No restaurants after filtering."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _filter_by_area(restaurants: list[Restaurant], area: str) -> list[Restaurant]:
    key = area.strip().casefold()
    if not key:
        return restaurants
    return [
        r
        for r in restaurants
        if key in str(r.attributes.get("area", "")).casefold()
        or key in str(r.attributes.get("listed_in", "")).casefold()
    ]


def _build_integration_scoped(
    preferences: UserPreferences,
    restaurants: list[Restaurant],
    settings: Settings,
) -> IntegrationResult:
    candidates, stats, no_match = build_candidate_set(
        preferences,
        restaurants,
        settings=settings,
    )
    context, context_json = build_llm_context_json(candidates, preferences)
    system_prompt, user_prompt = build_prompts(
        preferences,
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


def recommend(
    request: RecommendationRequest,
    repository: RestaurantRepositoryPort,
    *,
    settings: Settings | None = None,
) -> RecommendationResponse:
    """Full pipeline: validate → filter → Groq → response DTO."""
    settings = settings or get_settings()

    area = (request.area or "").strip() or None
    budget_inr = request.budget_inr
    payload = request.model_dump(exclude={"area", "budget_inr"})
    if area:
        extra = f"Prefer {area} area."
        if payload.get("additional"):
            payload["additional"] = f"{extra} {payload['additional']}"
        else:
            payload["additional"] = extra

    with log_phase("validate"):
        preferences = validate_json(
            payload,
            known_locations=repository.get_known_locations(),
        )

    with log_phase("integrate", location=preferences.location, area=area or ""):
        if area:
            restaurants = repository.filter_by_location(preferences.location)
            restaurants = _filter_by_area(restaurants, area)
            if not restaurants:
                raise NoMatchError(
                    f"No restaurants found in {area} ({preferences.location})."
                )
            integration = _build_integration_scoped(preferences, restaurants, settings)
        else:
            integration = run_integration(preferences, repository, settings=settings)

        if not integration.has_candidates:
            raise NoMatchError(
                integration.no_match_message
                or "No restaurants match your preferences."
            )

    with log_phase("engine", candidates=len(integration.candidates)):
        engine: EngineResult = run_recommendation(
            integration,
            repository,
            settings=settings,
        )

    return _to_response(
        engine,
        preferences,
        area,
        integration.filter_stats,
        budget_inr=budget_inr,
        cached=False,
    )


def _to_response(
    engine: EngineResult,
    preferences: UserPreferences,
    area: str | None,
    stats: FilterStats,
    *,
    budget_inr: int | None,
    cached: bool,
) -> RecommendationResponse:
    return RecommendationResponse(
        ok=True,
        source=engine.source,
        warning=engine.warning,
        summary=engine.result.summary,
        preferences=PreferencesDTO(
            location=preferences.location,
            budget=preferences.budget.value,
            cuisines=preferences.cuisines,
            min_rating=preferences.min_rating,
            additional=preferences.additional,
            area=area,
            budget_inr=budget_inr,
        ),
        filter_stats=FilterStatsDTO(
            location_count=stats.location_count,
            after_rating=stats.after_rating,
            after_cuisine=stats.after_cuisine,
            after_budget=stats.after_budget,
            after_top_k=stats.after_top_k,
        ),
        recommendations=[
            RecommendationItemDTO(
                restaurant_id=item.restaurant_id,
                rank=item.rank,
                name=item.name,
                cuisines=item.cuisines,
                rating=item.rating,
                estimated_cost=item.estimated_cost,
                explanation=item.explanation,
            )
            for item in engine.displays
        ],
        cached=cached,
    )
