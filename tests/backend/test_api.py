import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.models import Restaurant
from zm.models.enums import PriceBand


@pytest.fixture
def api_client():
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
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health(api_client: TestClient):
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data_loaded"] is True
    assert body["restaurant_count"] == 1
    assert "groq_configured" in body
    assert body["version"] == "0.1.0"


def test_service_root(api_client: TestClient):
    response = api_client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "zm-restaurant-api"
    assert body["health"] == "/health"


def test_api_discovery(api_client: TestClient):
    response = api_client.get("/api/v1")
    assert response.status_code == 200
    assert "locations" in response.json()["endpoints"]


def test_not_found_includes_hint(api_client: TestClient):
    response = api_client.get("/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Not Found"
    assert "try" in body
    assert body["try"]["health"] == "/health"


def test_locations(api_client: TestClient):
    response = api_client.get("/api/v1/locations")
    assert response.status_code == 200
    assert response.json()["locations"] == ["Bangalore"]


def test_metadata(api_client: TestClient):
    response = api_client.get("/api/v1/metadata")
    assert response.status_code == 200
    body = response.json()
    assert "low" in body["budgets"]
    assert body["display_top_n"] >= 1
    assert body["budget_inr_bands"]["low_max"] > 0


def test_recommendations_valid(api_client: TestClient):
    response = api_client.post(
        "/api/v1/recommendations",
        json={
            "location": "Bangalore",
            "budget": "medium",
            "cuisines": ["Italian"],
            "min_rating": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["source"] in ("groq", "fallback")
    assert len(body["recommendations"]) >= 1
    assert body["recommendations"][0]["name"] == "Test Rest"


def test_recommendations_invalid_location(api_client: TestClient):
    response = api_client.post(
        "/api/v1/recommendations",
        json={
            "location": "Delhi",
            "budget": "low",
            "cuisines": ["Chinese"],
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert "location" in body["errors"]
