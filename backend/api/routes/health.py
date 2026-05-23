"""Health and metadata routes (Phase 5a)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.deps import get_app_settings, get_restaurant_repository
from backend.api.schemas import (
    BudgetInrBandsDTO,
    HealthResponse,
    LocationsResponse,
    MetadataResponse,
)
from backend.services.budget_mapper import LOW_MAX, MEDIUM_MAX
from zm.config import Settings
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.exceptions import DataLoadError

router = APIRouter(tags=["health"])


def _optional_repository() -> RestaurantRepository | None:
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return holder.repository
    return None


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    repo = _optional_repository()
    ready = repo is not None and repo.is_ready()
    return HealthResponse(
        status="ok",
        data_loaded=ready,
        restaurant_count=repo.count() if ready and repo else 0,
    )


@router.get("/api/v1/locations", response_model=LocationsResponse)
def list_locations(
    repo: RestaurantRepository = Depends(get_restaurant_repository),
) -> LocationsResponse:
    return LocationsResponse(locations=repo.get_known_locations())


@router.get("/api/v1/metadata", response_model=MetadataResponse)
def metadata(
    settings: Settings = Depends(get_app_settings),
) -> MetadataResponse:
    return MetadataResponse(
        budgets=["low", "medium", "high"],
        example_cuisines=[
            "North Indian",
            "Chinese",
            "Italian",
            "South Indian",
            "Continental",
        ],
        display_top_n=settings.display_top_n,
        budget_inr_bands=BudgetInrBandsDTO(
            low_max=LOW_MAX,
            medium_max=MEDIUM_MAX,
            description=(
                f"≤₹{LOW_MAX} → low, ₹{LOW_MAX + 1}–₹{MEDIUM_MAX} → medium, "
                f">₹{MEDIUM_MAX} → high (for two)"
            ),
        ),
    )
