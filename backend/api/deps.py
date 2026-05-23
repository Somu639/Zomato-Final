"""FastAPI dependencies (Phase 5a)."""

from __future__ import annotations

from backend.data_loader import load_repository_full
from zm.config import Settings, get_settings
from zm.data.repository import RestaurantRepository
from zm.exceptions import DataLoadError


def get_app_settings() -> Settings:
    return get_settings()


def get_restaurant_repository() -> RestaurantRepository:
    try:
        return load_repository_full()
    except DataLoadError as exc:
        raise DataLoadError(
            "Restaurant data is not available. Run `zm load-data` first."
        ) from exc
