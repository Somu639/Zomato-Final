"""Restaurant data loading for API startup (Phase 7 — Render-safe)."""

from __future__ import annotations

import logging
import threading

from zm.config import Settings, get_settings
from zm.data.cache import cache_is_valid, load_cache
from zm.data.pipeline import build_repository
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.exceptions import DataLoadError

logger = logging.getLogger(__name__)

_prefetch_lock = threading.Lock()
_prefetch_started = False


def load_repository_from_cache_only(
    settings: Settings | None = None,
) -> RestaurantRepository | None:
    """Load restaurants from on-disk cache only (no Hugging Face download)."""
    settings = settings or get_settings()
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return holder.repository

    try:
        cache_dir = settings.ensure_cache_dir()
    except Exception as exc:
        logger.warning("Cache directory unavailable: %s", exc)
        return None

    cached, meta = load_cache(cache_dir)
    if not cached or not cache_is_valid(meta, settings.hf_dataset_id):
        return None

    repo = RestaurantRepository(cached)
    holder.set(repo)
    logger.info("Loaded %s restaurants from cache", repo.count())
    return repo


def load_repository_full(settings: Settings | None = None) -> RestaurantRepository:
    """Load from cache or download from Hugging Face."""
    settings = settings or get_settings()
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return holder.repository

    cached = load_repository_from_cache_only(settings)
    if cached is not None:
        return cached

    settings.ensure_cache_dir()
    repo = build_repository(settings)
    holder.set(repo)
    logger.info("Built repository with %s restaurants", repo.count())
    return repo


def prefetch_repository_in_background(settings: Settings | None = None) -> None:
    """Start a one-time background download/build (Render deploy must not block)."""
    global _prefetch_started
    settings = settings or get_settings()

    with _prefetch_lock:
        if _prefetch_started:
            return
        _prefetch_started = True

    def _run() -> None:
        try:
            load_repository_full(settings)
        except DataLoadError as exc:
            logger.warning("Background dataset prefetch failed: %s", exc)
        except Exception:
            logger.exception("Background dataset prefetch error")

    thread = threading.Thread(target=_run, name="dataset-prefetch", daemon=True)
    thread.start()
    logger.info("Background dataset prefetch started")
