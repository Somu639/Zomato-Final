"""Recommendation models (Phase 0 contract for Phase 4–5)."""

from pydantic import BaseModel, Field, field_validator


class Recommendation(BaseModel):
    """Single LLM-ranked recommendation mapped back to a restaurant."""

    restaurant_id: str = Field(min_length=1)
    rank: int = Field(ge=1)
    explanation: str = Field(min_length=1)

    model_config = {"frozen": True, "extra": "forbid"}


class RecommendationResult(BaseModel):
    """Full LLM response after parsing."""

    recommendations: list[Recommendation] = Field(min_length=1)
    summary: str | None = None

    @field_validator("recommendations")
    @classmethod
    def sort_by_rank(
        cls, value: list[Recommendation]
    ) -> list[Recommendation]:
        return sorted(value, key=lambda item: item.rank)

    model_config = {"frozen": True, "extra": "forbid"}


class RecommendationDisplay(BaseModel):
    """Enriched result for UI (Phase 5); merges dataset + LLM fields."""

    restaurant_id: str
    rank: int = Field(ge=1)
    name: str
    cuisines: list[str]
    rating: float | None
    estimated_cost: str
    explanation: str

    model_config = {"frozen": True, "extra": "forbid"}
