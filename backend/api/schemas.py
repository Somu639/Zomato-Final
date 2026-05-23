"""API request/response DTOs (Phase 5a / 6)."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from backend.services.budget_mapper import inr_for_two_to_band


class RecommendationRequest(BaseModel):
    location: str = Field(min_length=1, description="City, e.g. Bangalore")
    budget: str | None = Field(
        default=None,
        description="low | medium | high (optional if budget_inr set)",
    )
    budget_inr: int | None = Field(
        default=None,
        ge=100,
        le=50000,
        description="Budget for two in INR; maps to budget band (Phase 6)",
    )
    cuisines: list[str] | str = Field(description="One or more cuisines")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional: str | None = Field(default=None, max_length=500)
    area: str | None = Field(
        default=None,
        description="Optional area/neighborhood, e.g. Bellandur",
    )

    @model_validator(mode="after")
    def resolve_budget(self) -> RecommendationRequest:
        if self.budget_inr is not None:
            band = inr_for_two_to_band(self.budget_inr)
            object.__setattr__(self, "budget", band.value)
        elif not self.budget or not str(self.budget).strip():
            raise ValueError("Provide budget (low/medium/high) or budget_inr")
        return self


class FilterStatsDTO(BaseModel):
    location_count: int
    after_rating: int
    after_cuisine: int
    after_budget: int
    after_top_k: int


class PreferencesDTO(BaseModel):
    location: str
    budget: str
    cuisines: list[str]
    min_rating: float
    additional: str | None = None
    area: str | None = None
    budget_inr: int | None = None


class RecommendationItemDTO(BaseModel):
    restaurant_id: str
    rank: int
    name: str
    cuisines: list[str]
    rating: float | None
    estimated_cost: str
    explanation: str


class RecommendationResponse(BaseModel):
    ok: bool = True
    source: str
    warning: str | None = None
    summary: str | None = None
    preferences: PreferencesDTO
    filter_stats: FilterStatsDTO
    recommendations: list[RecommendationItemDTO]
    cached: bool = False


class ErrorResponse(BaseModel):
    ok: bool = False
    message: str = "Please fix the errors below."
    errors: dict[str, str] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    restaurant_count: int = 0


class LocationsResponse(BaseModel):
    locations: list[str]


class BudgetInrBandsDTO(BaseModel):
    low_max: int
    medium_max: int
    description: str


class MetadataResponse(BaseModel):
    budgets: list[str]
    example_cuisines: list[str]
    display_top_n: int
    budget_inr_bands: BudgetInrBandsDTO
