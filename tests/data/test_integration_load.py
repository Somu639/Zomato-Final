"""Optional live test against Hugging Face (skipped by default)."""

import pytest

from zm.config import Settings
from zm.data.pipeline import build_repository


@pytest.mark.integration
def test_build_repository_from_huggingface(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASET_CACHE_DIR", str(tmp_path))
    settings = Settings()
    repo = build_repository(settings, force_refresh=True)
    assert repo.is_ready()
    assert repo.count() > 0
    locations = repo.get_known_locations()
    assert "Bangalore" in locations
