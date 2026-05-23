import json

from zm.engine.pipeline import run_recommendation
from zm.integration.types import FilterStats, IntegrationResult
from zm.models import Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


class _MockGroq:
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "summary": "AI picks",
                "recommendations": [
                    {
                        "restaurant_id": "2",
                        "rank": 1,
                        "explanation": "Best Italian in town for your budget.",
                    }
                ],
            }
        )


class _FakeRepo:
    def filter_by_location(self, location: str) -> list[Restaurant]:
        return []

    def is_ready(self) -> bool:
        return True


def _integration() -> IntegrationResult:
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Italian"],
    )
    candidates = [
        Restaurant(
            id="1",
            name="Alpha",
            location="Bangalore",
            cuisines=["Chinese"],
            price_band=PriceBand.MEDIUM,
            rating=4.0,
        ),
        Restaurant(
            id="2",
            name="Beta",
            location="Bangalore",
            cuisines=["Italian"],
            price_band=PriceBand.MEDIUM,
            rating=4.6,
            cost_for_two=600,
        ),
    ]
    return IntegrationResult(
        preferences=prefs,
        candidates=candidates,
        context={},
        context_json="{}",
        prompt_version="v1",
        system_prompt="system",
        user_prompt="user",
        filter_stats=FilterStats(2, 2, 2, 2, 2),
    )


def test_run_recommendation_uses_groq_when_client_provided(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    result = run_recommendation(
        _integration(),
        _FakeRepo(),
        client=_MockGroq(),
    )
    assert result.source == "groq"
    assert result.displays[0].name == "Beta"
    assert "Italian" in result.displays[0].explanation


def test_run_recommendation_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    result = run_recommendation(_integration(), _FakeRepo())
    assert result.source == "fallback"
    assert result.warning is not None
    assert len(result.displays) >= 1
