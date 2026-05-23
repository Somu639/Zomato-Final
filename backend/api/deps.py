"""FastAPI dependencies (Phase 5a)."""

from __future__ import annotations

from zm.config import Settings, get_settings
from zm.data.pipeline import build_repository
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.exceptions import DataLoadError


def get_app_settings() -> Settings:
    return get_settings()


def get_restaurant_repository() -> RestaurantRepository:
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return holder.repository

    settings = get_settings()
    settings.ensure_cache_dir()
    try:
        repo = build_repository(settings)
    except DataLoadError as exc:
        raise DataLoadError(
            "Restaurant data is not available. Run `zm load-data` first."
        ) from exc

    holder.set(repo)
    return repo
