import pytest
from pydantic import ValidationError

from zm.models import (
    BudgetBand,
    Recommendation,
    RecommendationResult,
    Restaurant,
    UserPreferences,
)
from zm.models.enums import PriceBand


def test_user_preferences_from_comma_separated_cuisine():
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisines="Italian, chinese, Italian",
    )
    assert prefs.budget == BudgetBand.LOW
    assert prefs.cuisines == ["Italian", "chinese"]


def test_user_preferences_rejects_blank_location():
    with pytest.raises(ValidationError):
        UserPreferences(location="   ", budget="medium", cuisines=["Thai"])


def test_user_preferences_rejects_invalid_budget():
    with pytest.raises(ValidationError):
        UserPreferences(location="Delhi", budget="cheap", cuisines=["Thai"])


def test_user_preferences_rejects_rating_out_of_range():
    with pytest.raises(ValidationError):
        UserPreferences(
            location="Delhi",
            budget="medium",
            cuisines=["Thai"],
            min_rating=6.0,
        )


def test_restaurant_rating_bounds():
    with pytest.raises(ValidationError):
        Restaurant(
            id="1",
            name="Test",
            location="Delhi",
            cuisines=["Indian"],
            rating=5.5,
        )


def test_restaurant_parses_cuisine_string():
    rest = Restaurant(
        id="1",
        name="Test",
        location="Delhi",
        cuisines="North Indian, Chinese",
    )
    assert rest.cuisines == ["North Indian", "Chinese"]


def test_recommendation_result_sorts_by_rank():
    result = RecommendationResult(
        recommendations=[
            Recommendation(
                restaurant_id="b",
                rank=2,
                explanation="Second",
            ),
            Recommendation(
                restaurant_id="a",
                rank=1,
                explanation="First",
            ),
        ]
    )
    assert [item.restaurant_id for item in result.recommendations] == ["a", "b"]


def test_models_are_frozen():
    prefs = UserPreferences(
        location="Delhi",
        budget=BudgetBand.HIGH,
        cuisines=["Italian"],
    )
    with pytest.raises(ValidationError):
        prefs.location = "Mumbai"  # type: ignore[misc]
