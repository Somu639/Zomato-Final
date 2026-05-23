"""Health and metadata routes (Phase 5a)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.deps import get_app_settings, get_restaurant_repository
from backend.data_loader import load_repository_from_cache_only
from backend.api.schemas import (
    BudgetInrBandsDTO,
    HealthResponse,
    LocationsResponse,
    MetadataResponse,
    ServiceInfoResponse,
)
from zm import __version__
from backend.services.budget_mapper import LOW_MAX, MEDIUM_MAX
from zm.config import Settings
from zm.data.repository import RestaurantRepository, get_repository_holder

router = APIRouter(tags=["health"])


def _repository_status() -> tuple[bool, int]:
    """Return (data_loaded, restaurant_count) without blocking on HF download."""
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return True, holder.repository.count()
    repo = load_repository_from_cache_only()
    if repo is not None:
        return True, repo.count()
    return False, 0


@router.get("/", response_model=ServiceInfoResponse, include_in_schema=False)
def service_root() -> ServiceInfoResponse:
    return ServiceInfoResponse(
        service="zm-restaurant-api",
        version=__version__,
        docs="/docs",
        health="/health",
        openapi="/openapi.json",
    )


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    ready, count = _repository_status()
    return HealthResponse(
        status="ok",
        data_loaded=ready,
        restaurant_count=count,
        groq_configured=settings.has_groq_api_key,
        version=__version__,
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
