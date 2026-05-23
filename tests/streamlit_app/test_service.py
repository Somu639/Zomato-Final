import pytest

from streamlit_app.service import NoMatchError, PreferenceInput, recommend, inr_for_two_to_band
from zm.data.repository import RestaurantRepository
from zm.models import Restaurant
from zm.models.enums import BudgetBand, PriceBand


@pytest.fixture
def repo():
    return RestaurantRepository(
        [
            Restaurant(
                id="1",
                name="Test Rest",
                location="Bangalore",
                cuisines=["Italian"],
                price_band=PriceBand.MEDIUM,
                rating=4.0,
            )
        ]
    )


def test_inr_to_band():
    assert inr_for_two_to_band(500) == BudgetBand.LOW
    assert inr_for_two_to_band(2000) == BudgetBand.MEDIUM
    assert inr_for_two_to_band(3000) == BudgetBand.HIGH


def test_recommend_success(repo):
    outcome = recommend(
        PreferenceInput(
            location="Bangalore",
            cuisines=["Italian"],
            min_rating=3.0,
            budget="medium",
        ),
        repo,
    )
    assert len(outcome.engine.displays) >= 1
    assert outcome.engine.displays[0].name == "Test Rest"


def test_recommend_no_match_city(repo):
    with pytest.raises(NoMatchError):
        recommend(
            PreferenceInput(
                location="Bangalore",
                cuisines=["Japanese"],
                min_rating=4.5,
                budget="low",
            ),
            repo,
        )
