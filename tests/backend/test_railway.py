"""Railway / production deployment settings (Phase 7)."""

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from zm.config import clear_settings_cache
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.models import Restaurant
from zm.models.enums import PriceBand


@pytest.fixture
def railway_client(monkeypatch):
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    clear_settings_cache()
    repo = RestaurantRepository(
        [
            Restaurant(
                id="1",
                name="Test Rest",
                location="Bangalore",
                cuisines=["Italian"],
                price_band=PriceBand.MEDIUM,
                rating=4.0,
            )
        ]
    )
    get_repository_holder().set(repo)
    with TestClient(create_app()) as client:
        yield client


def test_health_on_railway(railway_client: TestClient):
    response = railway_client.get("/health")
    assert response.status_code == 200
    assert response.json()["data_loaded"] is True
