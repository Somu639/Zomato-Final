from zm.integration.filters import (
    apply_hard_filters,
    matches_budget,
    matches_cuisine,
    matches_rating,
)
from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


def _restaurant(**kwargs) -> Restaurant:
    defaults = {
        "id": "1",
        "name": "Test",
        "location": "Bangalore",
        "cuisines": ["North Indian"],
        "price_band": PriceBand.MEDIUM,
        "rating": 4.0,
        "cost_for_two": 500,
    }
    defaults.update(kwargs)
    return Restaurant(**defaults)


def test_matches_cuisine_or_semantics():
    r = _restaurant(cuisines=["North Indian", "Chinese"])
    assert matches_cuisine(r, ["Chinese"])
    assert not matches_cuisine(r, ["Italian"])


def test_matches_budget_unknown_is_permissive():
    r = _restaurant(price_band=PriceBand.UNKNOWN)
    assert matches_budget(r, BudgetBand.LOW)


def test_apply_hard_filters_pipeline():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Indian"],
        min_rating=3.5,
    )
    restaurants = [
        _restaurant(id="a", rating=4.5, cuisines=["North Indian"]),
        _restaurant(id="b", rating=3.0, cuisines=["North Indian"]),
        _restaurant(id="c", rating=4.0, cuisines=["Italian"]),
        _restaurant(id="d", rating=4.0, price_band=PriceBand.HIGH),
    ]
    filtered, stats = apply_hard_filters(restaurants, prefs)
    assert stats.location_count == 4
    assert stats.after_rating == 3
    assert "a" in {r.id for r in filtered}
    assert "b" not in {r.id for r in filtered}
    assert "c" not in {r.id for r in filtered}
