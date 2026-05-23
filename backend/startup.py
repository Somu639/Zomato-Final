"""Application startup helpers (Phase 7 — Render / production)."""

from __future__ import annotations

import logging

from backend.api.deps import get_restaurant_repository
from zm.config import Settings, get_settings
from zm.exceptions import DataLoadError

logger = logging.getLogger(__name__)


def bootstrap_repository(settings: Settings | None = None) -> int | None:
    """
    Load the restaurant repository into the process holder.

    Returns restaurant count on success, or None if data is unavailable.
    """
    settings = settings or get_settings()
    try:
        repo = get_restaurant_repository()
        count = repo.count()
        logger.info("Restaurant repository ready (%s restaurants)", count)
        return count
    except DataLoadError as exc:
        logger.warning("Restaurant data not available at startup: %s", exc)
        return None


def log_deployment_context(settings: Settings) -> None:
    """Log non-secret settings useful on Render deploys."""
    summary = settings.redacted_summary()
    logger.info("Deployment context: %s", summary)
    if settings.is_render and not settings.cors_origins_list:
        logger.warning(
            "CORS_ORIGINS is empty on Render — set your Vercel URL "
            "(see Docs/Deployment-Render-Vercel.md)"
        )
    if settings.is_render and settings.has_only_local_cors_origins:
        logger.warning(
            "CORS_ORIGINS still lists only localhost — add your Vercel "
            "production URL before going live"
        )
