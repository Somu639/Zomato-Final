from backend.api.schemas import (
    FilterStatsDTO,
    PreferencesDTO,
    RecommendationItemDTO,
    RecommendationResponse,
)
from backend.cache.recommendation_cache import RecommendationCache


def _sample_response() -> RecommendationResponse:
    return RecommendationResponse(
        ok=True,
        source="fallback",
        preferences=PreferencesDTO(
            location="Bangalore",
            budget="medium",
            cuisines=["Italian"],
            min_rating=4.0,
        ),
        filter_stats=FilterStatsDTO(
            location_count=10,
            after_rating=8,
            after_cuisine=5,
            after_budget=3,
            after_top_k=3,
        ),
        recommendations=[
            RecommendationItemDTO(
                restaurant_id="1",
                rank=1,
                name="Test",
                cuisines=["Italian"],
                rating=4.0,
                estimated_cost="₹800",
                explanation="Good fit",
            )
        ],
    )


def test_cache_hit_and_miss():
    cache = RecommendationCache(ttl_seconds=60)
    key = cache.make_key({"location": "Bangalore", "budget": "low"})
    assert cache.get(key) is None
    cache.set(key, _sample_response())
    hit = cache.get(key)
    assert hit is not None
    assert hit.source == "fallback"


def test_cache_disabled_when_ttl_zero():
    cache = RecommendationCache(ttl_seconds=0)
    key = cache.make_key({"a": 1})
    cache.set(key, _sample_response())
    assert cache.get(key) is None
