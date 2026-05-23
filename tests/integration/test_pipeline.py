from zm.integration.pipeline import build_candidate_set, run_integration
from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


def _make_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="1",
            name="Alpha",
            location="Bangalore",
            cuisines=["Italian"],
            price_band=PriceBand.MEDIUM,
            rating=4.5,
            cost_for_two=600,
        ),
        Restaurant(
            id="2",
            name="Beta",
            location="Bangalore",
            cuisines=["Chinese"],
            price_band=PriceBand.LOW,
            rating=4.0,
            cost_for_two=200,
        ),
        Restaurant(
            id="3",
            name="Gamma",
            location="Bangalore",
            cuisines=["Italian"],
            price_band=PriceBand.HIGH,
            rating=4.8,
            cost_for_two=1200,
        ),
    ]


class _FakeRepo:
    def filter_by_location(self, location: str) -> list[Restaurant]:
        return [r for r in _make_restaurants() if r.location == location]

    def is_ready(self) -> bool:
        return True


def test_build_candidate_set_top_k():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Italian"],
        min_rating=4.0,
    )
    candidates, stats, msg = build_candidate_set(
        prefs,
        _make_restaurants(),
        top_k=1,
    )
    assert msg is None
    assert len(candidates) == 1
    assert stats.after_top_k == 1
    assert candidates[0].id == "1"


def test_no_match_message():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.LOW,
        cuisines=["Mexican"],
        min_rating=4.5,
    )
    candidates, stats, msg = build_candidate_set(prefs, _make_restaurants())
    assert candidates == []
    assert msg is not None
    assert "No restaurants" in msg


def test_run_integration_builds_prompt():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Italian"],
        min_rating=4.0,
    )
    result = run_integration(prefs, _FakeRepo())
    assert result.has_candidates
    assert result.prompt_version == "v1"
    assert "restaurant_id" in result.context_json
    assert len(result.system_prompt) > 0
    assert len(result.user_prompt) > 0
