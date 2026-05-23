"""Tests for Render-safe data loading."""

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from zm.config import clear_settings_cache
from zm.data.repository import get_repository_holder


@pytest.fixture
def empty_client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATASET_CACHE_DIR", str(tmp_path / "empty_cache"))
    monkeypatch.setenv("RENDER", "true")
    clear_settings_cache()
    holder = get_repository_holder()
    with holder._lock:
        holder._repository = None
    with TestClient(create_app()) as client:
        yield client


def test_health_returns_200_before_data_loaded(empty_client: TestClient):
    response = empty_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data_loaded"] is False
    assert body["restaurant_count"] == 0
