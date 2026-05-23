"""Hard filters: location, rating, cuisine, budget."""

from __future__ import annotations

from zm.integration.types import FilterStats
from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


def matches_rating(restaurant: Restaurant, min_rating: float) -> bool:
    """Exclude unknown ratings when a minimum is required (P1-10, P3-05)."""
    if min_rating <= 0:
        return True
    if restaurant.rating is None:
        return False
    return restaurant.rating >= min_rating


def matches_cuisine(restaurant: Restaurant, preferred: list[str]) -> bool:
    """True if any preferred cuisine overlaps a restaurant tag (OR semantics, P2-09)."""
    if not preferred:
        return True

    pref_tokens = [c.casefold() for c in preferred]
    for tag in restaurant.cuisines:
        tag_fold = tag.casefold()
        for pref in pref_tokens:
            if pref in tag_fold or tag_fold in pref:
                return True
    return False


def matches_budget(restaurant: Restaurant, budget: BudgetBand) -> bool:
    """
    Match restaurant price band to user budget.

    ``UNKNOWN`` price bands are included for any user budget (P3-11).
    """
    band = restaurant.price_band
    if band == PriceBand.UNKNOWN:
        return True
    return band.value == budget.value


def apply_hard_filters(
    restaurants: list[Restaurant],
    preferences: UserPreferences,
) -> tuple[list[Restaurant], FilterStats]:
    """
    Apply rating, cuisine, and budget filters.

    Location should already be applied by the caller via the repository.
    """
    location_count = len(restaurants)

    after_rating = [r for r in restaurants if matches_rating(r, preferences.min_rating)]
    after_cuisine = [r for r in after_rating if matches_cuisine(r, preferences.cuisines)]
    after_budget = [r for r in after_cuisine if matches_budget(r, preferences.budget)]

    stats = FilterStats(
        location_count=location_count,
        after_rating=len(after_rating),
        after_cuisine=len(after_cuisine),
        after_budget=len(after_budget),
        after_top_k=len(after_budget),
    )
    return after_budget, stats
