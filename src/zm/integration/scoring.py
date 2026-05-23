"""Soft ranking before Top-K truncation."""

from __future__ import annotations

from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


def _budget_fit_score(restaurant: Restaurant, budget: BudgetBand) -> float:
    band = restaurant.price_band
    if band == PriceBand.UNKNOWN:
        return 0.5
    if band.value == budget.value:
        return 2.0
    return 0.0


def score_restaurant(restaurant: Restaurant, preferences: UserPreferences) -> float:
    """Higher is better. Rating weighted above budget fit."""
    rating_part = restaurant.rating if restaurant.rating is not None else 0.0
    return rating_part * 2.0 + _budget_fit_score(restaurant, preferences.budget)


def rank_candidates(
    restaurants: list[Restaurant],
    preferences: UserPreferences,
) -> list[Restaurant]:
    """Stable sort by soft score descending, then by id."""
    return sorted(
        restaurants,
        key=lambda r: (-score_restaurant(r, preferences), r.id),
    )
