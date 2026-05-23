from pathlib import Path

import pytest

from zm.data.cache import cache_is_valid, load_cache, save_cache
from zm.data.pipeline import ingest_from_csv
from zm.data.preprocessor import PreprocessStats
from zm.data.repository import RestaurantRepository
from tests.data.fixtures import write_sample_csv


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "zomato.csv"
    write_sample_csv(path)
    return path


def test_ingest_from_csv(sample_csv: Path):
    restaurants, stats = ingest_from_csv(sample_csv)
    assert stats.input_count == 5
    assert stats.skipped_invalid >= 1
    assert len(restaurants) >= 2
    cities = {r.location for r in restaurants}
    assert "Bangalore" in cities


def test_repository_filter_by_location(sample_csv: Path):
    restaurants, _ = ingest_from_csv(sample_csv)
    repo = RestaurantRepository(restaurants)
    assert repo.is_ready()
    blr = repo.filter_by_location("bangalore")
    assert len(blr) >= 1
    assert repo.get_known_locations()
    first = blr[0]
    assert repo.get_by_id(first.id) == first
    assert repo.get_by_id("missing") is None


def test_cache_roundtrip(tmp_path: Path, sample_csv: Path):
    restaurants, stats = ingest_from_csv(sample_csv)
    save_cache(
        tmp_path,
        restaurants,
        hf_dataset_id="test/dataset",
        source_file="zomato.csv",
        stats=stats,
    )
    loaded, meta = load_cache(tmp_path)
    assert len(loaded) == len(restaurants)
    assert meta is not None
    assert cache_is_valid(meta, "test/dataset")
    assert not cache_is_valid(meta, "other/dataset")
