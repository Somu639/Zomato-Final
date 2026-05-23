"""Persist normalized restaurants as JSONL + metadata."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from zm.data.constants import CACHE_META_FILE, CACHE_RESTAURANTS_FILE, CACHE_VERSION
from zm.data.preprocessor import PreprocessStats
from zm.exceptions import DataLoadError
from zm.models import Restaurant

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CacheMeta:
    version: str
    hf_dataset_id: str
    source_file: str
    restaurant_count: int
    generated_at: str
    preprocess: dict[str, int]


def cache_paths(cache_dir: Path) -> tuple[Path, Path]:
    return cache_dir / CACHE_RESTAURANTS_FILE, cache_dir / CACHE_META_FILE


def save_cache(
    cache_dir: Path,
    restaurants: list[Restaurant],
    *,
    hf_dataset_id: str,
    source_file: str,
    stats: PreprocessStats,
) -> tuple[Path, Path]:
    """Write JSONL cache and metadata sidecar."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    data_path, meta_path = cache_paths(cache_dir)

    try:
        with data_path.open("w", encoding="utf-8") as handle:
            for restaurant in restaurants:
                handle.write(restaurant.model_dump_json())
                handle.write("\n")

        meta = CacheMeta(
            version=CACHE_VERSION,
            hf_dataset_id=hf_dataset_id,
            source_file=source_file,
            restaurant_count=len(restaurants),
            generated_at=datetime.now(timezone.utc).isoformat(),
            preprocess={
                "input_count": stats.input_count,
                "output_count": stats.output_count,
                "skipped_invalid": stats.skipped_invalid,
                "duplicates_removed": stats.duplicates_removed,
            },
        )
        meta_path.write_text(
            json.dumps(asdict(meta), indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise DataLoadError(f"Cannot write cache under {cache_dir}: {exc}") from exc

    logger.info("Wrote %s restaurants to %s", len(restaurants), data_path)
    return data_path, meta_path


def load_cache(cache_dir: Path) -> tuple[list[Restaurant], CacheMeta | None]:
    """Load restaurants from JSONL cache if present."""
    data_path, meta_path = cache_paths(cache_dir)
    if not data_path.is_file():
        return [], None

    restaurants: list[Restaurant] = []
    try:
        with data_path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    restaurants.append(Restaurant.model_validate_json(line))
                except Exception as exc:
                    raise DataLoadError(
                        f"Invalid cache line {line_no} in {data_path}: {exc}"
                    ) from exc
    except OSError as exc:
        raise DataLoadError(f"Cannot read cache file {data_path}: {exc}") from exc

    meta: CacheMeta | None = None
    if meta_path.is_file():
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            meta = CacheMeta(**payload)
        except (OSError, TypeError, ValueError) as exc:
            logger.warning("Could not read cache metadata %s: %s", meta_path, exc)

    return restaurants, meta


def cache_is_valid(meta: CacheMeta | None, hf_dataset_id: str) -> bool:
    if meta is None:
        return False
    return meta.version == CACHE_VERSION and meta.hf_dataset_id == hf_dataset_id
