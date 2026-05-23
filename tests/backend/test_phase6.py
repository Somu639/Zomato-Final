import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.models import Restaurant
from zm.models.enums import PriceBand


@pytest.fixture
def client():
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
    with TestClient(create_app()) as test_client:
        yield test_client


def test_request_id_header(client: TestClient):
    response = client.get("/health", headers={"X-Request-ID": "test-req-1"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-req-1"


def test_recommendations_with_budget_inr(client: TestClient):
    response = client.post(
        "/api/v1/recommendations",
        json={
            "location": "Bangalore",
            "budget_inr": 2000,
            "cuisines": ["Italian"],
            "min_rating": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["preferences"]["budget"] == "medium"
    assert body["preferences"]["budget_inr"] == 2000


def test_metadata_budget_inr_bands(client: TestClient):
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    assert "budget_inr_bands" in response.json()
