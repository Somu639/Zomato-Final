"""Map recommendations to display DTOs (Phase 4/5 boundary)."""

from __future__ import annotations

from zm.models import Recommendation, RecommendationDisplay, Restaurant


def format_estimated_cost(restaurant: Restaurant) -> str:
    if restaurant.cost_for_two is not None:
        return f"₹{restaurant.cost_for_two:,} for two"
    if restaurant.price_band.value != "unknown":
        return restaurant.price_band.value.title()
    return "Not available"


def enrich_recommendation(
    item: Recommendation,
    restaurant: Restaurant,
) -> RecommendationDisplay:
    return RecommendationDisplay(
        restaurant_id=item.restaurant_id,
        rank=item.rank,
        name=restaurant.name,
        cuisines=restaurant.cuisines,
        rating=restaurant.rating,
        estimated_cost=format_estimated_cost(restaurant),
        explanation=item.explanation,
    )


def enrich_recommendations(
    recommendations: list[Recommendation],
    restaurants_by_id: dict[str, Restaurant],
) -> list[RecommendationDisplay]:
    """Build display rows; skip IDs missing from the repository (X-10)."""
    displays: list[RecommendationDisplay] = []
    for item in recommendations:
        restaurant = restaurants_by_id.get(item.restaurant_id)
        if restaurant is None:
            continue
        displays.append(enrich_recommendation(item, restaurant))
    return displays
