"""Application startup helpers (Phase 7 — Railway / production)."""

from __future__ import annotations

import logging

from backend.data_loader import (
    load_repository_from_cache_only,
    prefetch_repository_in_background,
)
from zm.config import Settings, get_settings

logger = logging.getLogger(__name__)


def bootstrap_repository(settings: Settings | None = None) -> int | None:
    """
    Fast startup: load cache if present; never block on Hugging Face download.

    On Railway, dataset download runs in a background thread after the server
    binds to PORT so deploy health checks pass quickly.
    """
    settings = settings or get_settings()
    repo = load_repository_from_cache_only(settings)
    if repo is not None:
        return repo.count()

    prefetch_repository_in_background(settings)
    logger.info(
        "No local cache yet; serving /health immediately while data loads in background"
    )
    return None


def log_deployment_context(settings: Settings) -> None:
    """Log non-secret settings useful on cloud deploys."""
    summary = settings.redacted_summary()
    logger.info("Deployment context: %s", summary)
    if settings.is_railway and not settings.cors_origins_list:
        logger.warning(
            "CORS_ORIGINS is empty on Railway — set your Vercel URL "
            "(see Docs/Deployment-Railway-Vercel.md)"
        )
    if settings.is_railway and settings.has_only_local_cors_origins:
        logger.warning(
            "CORS_ORIGINS still lists only localhost — add your Vercel "
            "production URL before going live"
        )
