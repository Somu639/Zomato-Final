"""Download and stream-parse the Hugging Face Zomato CSV."""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path
from typing import Any, Iterator

from huggingface_hub import hf_hub_download

from zm.config import Settings
from zm.data.constants import HF_DATASET_FILE
from zm.exceptions import DataLoadError

logger = logging.getLogger(__name__)


def _csv_field_limit() -> None:
    """Allow large ``reviews_list`` cells in the Zomato export."""
    csv.field_size_limit(sys.maxsize)


def download_dataset_csv(settings: Settings) -> Path:
    """
    Download ``zomato.csv`` from Hugging Face into the hub cache.

    Returns the local path to the CSV file.
    """
    try:
        path = hf_hub_download(
            repo_id=settings.hf_dataset_id,
            filename=HF_DATASET_FILE,
            repo_type="dataset",
        )
    except Exception as exc:
        raise DataLoadError(
            f"Could not download dataset '{settings.hf_dataset_id}' "
            f"({HF_DATASET_FILE}): {exc}"
        ) from exc

    csv_path = Path(path)
    if not csv_path.is_file() or csv_path.stat().st_size == 0:
        raise DataLoadError(f"Downloaded dataset file is missing or empty: {csv_path}")

    logger.info("Dataset CSV ready at %s (%s bytes)", csv_path, csv_path.stat().st_size)
    return csv_path


def iter_csv_rows(csv_path: Path) -> Iterator[dict[str, Any]]:
    """Yield raw dict rows from the Zomato CSV."""
    _csv_field_limit()
    try:
        with csv_path.open(encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DataLoadError(f"CSV has no header row: {csv_path}")
            yield from reader
    except DataLoadError:
        raise
    except OSError as exc:
        raise DataLoadError(f"Cannot read dataset CSV: {csv_path}") from exc
