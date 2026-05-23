"""Rule-based recommendations when Groq is unavailable or parsing fails."""

from __future__ import annotations

from zm.models import Recommendation, RecommendationResult, Restaurant, UserPreferences


def fallback_recommendations(
    candidates: list[Restaurant],
    preferences: UserPreferences,
    *,
    top_n: int = 5,
) -> RecommendationResult:
    """
    Rank by existing Phase 3 order (rating/budget score) with generic explanations.
    """
    selected = candidates[:top_n]
    recommendations: list[Recommendation] = []

    for index, restaurant in enumerate(selected, start=1):
        rating_text = (
            f"rating {restaurant.rating}"
            if restaurant.rating is not None
            else "rating not available"
        )
        explanation = (
            f"Matches your preferences for {preferences.location}, "
            f"{preferences.budget.value} budget, and {', '.join(preferences.cuisines)} "
            f"({rating_text}, {restaurant.price_band.value} price band). "
            "AI explanation unavailable — ranked by rating and budget fit."
        )
        recommendations.append(
            Recommendation(
                restaurant_id=restaurant.id,
                rank=index,
                explanation=explanation,
            )
        )

    summary = (
        f"Top {len(recommendations)} picks in {preferences.location} "
        "(rule-based ranking; Groq LLM was not used)."
    )
    return RecommendationResult(
        recommendations=recommendations,
        summary=summary,
    )
