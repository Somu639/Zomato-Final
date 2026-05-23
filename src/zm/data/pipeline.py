"""Orchestrate download, normalize, cache, and repository build."""

from __future__ import annotations

import logging
from pathlib import Path

from zm.config import Settings, get_settings
from zm.data.cache import cache_is_valid, load_cache, save_cache
from zm.data.constants import HF_DATASET_FILE
from zm.data.loader import download_dataset_csv, iter_csv_rows
from zm.data.normalizer import normalize_row
from zm.data.preprocessor import PreprocessStats, preprocess
from zm.data.repository import RestaurantRepository
from zm.exceptions import DataLoadError

logger = logging.getLogger(__name__)


def ingest_from_csv(csv_path: Path) -> tuple[list[Restaurant], PreprocessStats]:
    """Parse CSV, normalize rows, dedupe, and return stats."""
    from zm.models import Restaurant

    normalized: list[Restaurant] = []
    skipped = 0
    input_count = 0

    for index, row in enumerate(iter_csv_rows(csv_path)):
        input_count += 1
        restaurant = normalize_row(row, row_index=index)
        if restaurant is None:
            skipped += 1
            continue
        normalized.append(restaurant)

    if input_count == 0:
        raise DataLoadError("Dataset CSV contains no data rows")

    processed, stats = preprocess(
        normalized,
        input_count=input_count,
        skipped_invalid=skipped,
    )

    if not processed:
        raise DataLoadError(
            "No valid restaurants after preprocessing. "
            "Check dataset schema or normalizer."
        )

    return processed, stats


def build_repository(
    settings: Settings | None = None,
    *,
    force_refresh: bool = False,
) -> RestaurantRepository:
    """
    Load restaurants from cache or ingest from Hugging Face.

    Args:
        settings: Application settings.
        force_refresh: Re-download and rebuild cache even if valid cache exists.
    """
    settings = settings or get_settings()
    cache_dir = settings.ensure_cache_dir()

    if not force_refresh:
        cached, meta = load_cache(cache_dir)
        if cached and cache_is_valid(meta, settings.hf_dataset_id):
            logger.info("Using cached restaurants (%s rows)", len(cached))
            return RestaurantRepository(cached)

    csv_path = download_dataset_csv(settings)
    restaurants, stats = ingest_from_csv(csv_path)

    save_cache(
        cache_dir,
        restaurants,
        hf_dataset_id=settings.hf_dataset_id,
        source_file=HF_DATASET_FILE,
        stats=stats,
    )
    return RestaurantRepository(restaurants)
