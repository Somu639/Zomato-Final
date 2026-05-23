"""Clean, dedupe, and summarize normalized restaurant lists."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from zm.models import Restaurant

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreprocessStats:
    """Counts produced during preprocessing."""

    input_count: int
    output_count: int
    skipped_invalid: int
    duplicates_removed: int


def dedupe_restaurants(restaurants: list[Restaurant]) -> tuple[list[Restaurant], int]:
    """
    Remove duplicates keyed by name + city + address (attributes).

    When duplicates exist, keep the row with the higher rating (or first seen).
    """
    best: dict[tuple[str, str, str], Restaurant] = {}
    removed = 0

    for restaurant in restaurants:
        address = str(restaurant.attributes.get("address", ""))
        key = (
            restaurant.name.casefold(),
            restaurant.location.casefold(),
            address.casefold(),
        )
        existing = best.get(key)
        if existing is None:
            best[key] = restaurant
            continue

        removed += 1
        if _rating_score(restaurant) > _rating_score(existing):
            best[key] = restaurant

    return list(best.values()), removed


def _rating_score(restaurant: Restaurant) -> float:
    return restaurant.rating if restaurant.rating is not None else -1.0


def preprocess(
    restaurants: list[Restaurant],
    *,
    input_count: int,
    skipped_invalid: int,
) -> tuple[list[Restaurant], PreprocessStats]:
    """Apply deduplication and return stats."""
    deduped, removed = dedupe_restaurants(restaurants)
    stats = PreprocessStats(
        input_count=input_count,
        output_count=len(deduped),
        skipped_invalid=skipped_invalid,
        duplicates_removed=removed,
    )
    logger.info(
        "Preprocessed restaurants: %s valid, %s skipped, %s duplicates removed",
        stats.output_count,
        stats.skipped_invalid,
        stats.duplicates_removed,
    )
    return deduped, stats
