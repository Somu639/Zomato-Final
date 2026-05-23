"""Verify mock implementations satisfy runtime protocols (P0-09)."""

from zm.interfaces import LLMClientPort, RestaurantRepositoryPort, UserInterfacePort
from zm.models import RecommendationDisplay, Restaurant, UserPreferences
from zm.models.enums import BudgetBand, PriceBand


class MockRepository:
    def is_ready(self) -> bool:
        return True

    def get_all(self) -> list[Restaurant]:
        return []

    def filter_by_location(self, location: str) -> list[Restaurant]:
        return []

    def get_known_locations(self) -> list[str]:
        return ["Delhi"]

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        return None


class MockLLM:
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        return (
            '{"summary": "Mock", "recommendations": ['
            '{"restaurant_id": "r1", "rank": 1, "explanation": "Mock"}]}'
        )


class MockUI:
    def collect_preferences(self) -> UserPreferences:
        return UserPreferences(
            location="Delhi",
            budget=BudgetBand.LOW,
            cuisines=["Chinese"],
        )

    def display_results(
        self,
        results: list[RecommendationDisplay],
        *,
        summary: str | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        pass

    def display_error(self, message: str) -> None:
        pass

    def display_loading(self, message: str = "Finding recommendations…") -> None:
        pass


def test_mock_repository_is_port():
    assert isinstance(MockRepository(), RestaurantRepositoryPort)


def test_mock_llm_is_port():
    client = MockLLM()
    raw = client.complete(system_prompt="sys", user_prompt="user")
    assert isinstance(client, LLMClientPort)
    assert "r1" in raw


def test_mock_ui_is_port():
    assert isinstance(MockUI(), UserInterfacePort)


def test_sample_restaurant_contract():
    rest = Restaurant(
        id="abc",
        name="Sample",
        location="Bangalore",
        cuisines=["Italian"],
        price_band=PriceBand.MEDIUM,
        rating=4.2,
    )
    assert rest.id == "abc"
