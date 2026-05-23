from zm.integration.context import build_llm_context_json
from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


def test_context_json_shrinks_when_too_large():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Indian"],
    )
    restaurants = [
        Restaurant(
            id=str(i),
            name=f"Restaurant Number {i} With A Long Name",
            location="Bangalore",
            cuisines=["North Indian", "Chinese", "Mughlai"],
            price_band=PriceBand.MEDIUM,
            rating=4.0,
            cost_for_two=500,
            attributes={"area": "Area " * 20, "dish_liked": "x" * 200},
        )
        for i in range(50)
    ]
    _payload, text = build_llm_context_json(
        restaurants,
        prefs,
        max_chars=2000,
    )
    assert len(text) <= 2000
