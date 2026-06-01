"""In-process recommendation pipeline for Streamlit (Phase 7)."""

from __future__ import annotations

from dataclasses import dataclass

from zm.config import Settings, get_settings
from zm.engine.pipeline import run_recommendation
from zm.engine.types import EngineResult
from zm.exceptions import ValidationError
from zm.input.validator import validate_json
from zm.integration import run_integration
from zm.integration.context import build_llm_context_json
from zm.integration.pipeline import build_candidate_set
from zm.integration.prompts import PROMPT_VERSION, build_prompts
from zm.integration.types import FilterStats, IntegrationResult
from zm.interfaces.data_source import RestaurantRepositoryPort
from zm.models import Restaurant
from zm.models.enums import BudgetBand

_LOW_MAX = 600
_MEDIUM_MAX = 2000


class NoMatchError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class PreferenceInput:
    location: str
    cuisines: list[str] | str
    min_rating: float
    budget: str | None = None
    budget_inr: int | None = None
    additional: str | None = None
    area: str | None = None


@dataclass(frozen=True)
class RecommendOutcome:
    engine: EngineResult
    filter_stats: FilterStats
    area: str | None
    budget_inr: int | None


def inr_for_two_to_band(amount: int) -> BudgetBand:
    if amount <= _LOW_MAX:
        return BudgetBand.LOW
    if amount <= _MEDIUM_MAX:
        return BudgetBand.MEDIUM
    return BudgetBand.HIGH


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


def _build_integration_scoped(preferences, restaurants, settings: Settings):
    candidates, stats, no_match = build_candidate_set(
        preferences, restaurants, settings=settings
    )
    context, context_json = build_llm_context_json(candidates, preferences)
    system_prompt, user_prompt = build_prompts(
        preferences, context_json, display_top_n=settings.display_top_n
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


def _resolve_budget(inp: PreferenceInput) -> str:
    if inp.budget_inr is not None:
        return inr_for_two_to_band(inp.budget_inr).value
    if inp.budget and inp.budget.strip():
        return inp.budget.strip().lower()
    raise ValidationError(
        "Provide a budget band or amount in ₹",
        field_errors={"budget": "Select a budget band or enter ₹ for two"},
    )


def recommend(
    inp: PreferenceInput,
    repository: RestaurantRepositoryPort,
    *,
    settings: Settings | None = None,
) -> RecommendOutcome:
    settings = settings or get_settings()
    area = (inp.area or "").strip() or None
    budget_inr = inp.budget_inr

    payload: dict = {
        "location": inp.location,
        "budget": _resolve_budget(inp),
        "cuisines": inp.cuisines,
        "min_rating": inp.min_rating,
        "additional": inp.additional,
    }
    if area:
        extra = f"Prefer {area} area."
        payload["additional"] = (
            f"{extra} {payload['additional']}"
            if payload.get("additional")
            else extra
        )

    preferences = validate_json(
        payload, known_locations=repository.get_known_locations()
    )

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

    engine = run_recommendation(integration, repository, settings=settings)
    return RecommendOutcome(
        engine=engine,
        filter_stats=integration.filter_stats,
        area=area,
        budget_inr=budget_inr,
    )
