import pytest
from fastapi.testclient import TestClient

from zm.data.repository import RestaurantRepository, get_repository_holder
from zm.models import Restaurant
from zm.models.enums import PriceBand
from zm.web.app import create_app


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
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_get_form(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "Find restaurants" in response.text
    assert "Bangalore" in response.text


def test_post_form_valid(client: TestClient):
    response = client.post(
        "/recommendations",
        data={
            "location": "Bangalore",
            "budget": "medium",
            "cuisines": "Italian",
            "min_rating": "4",
            "additional": "",
        },
    )
    assert response.status_code == 200
    assert "recommendations" in response.text.lower() or "Top" in response.text
    assert "Italian" in response.text


def test_post_form_invalid_budget(client: TestClient):
    response = client.post(
        "/recommendations",
        data={
            "location": "Bangalore",
            "budget": "cheap",
            "cuisines": "Italian",
        },
    )
    assert response.status_code == 200
    assert "budget" in response.text.lower() or "one of" in response.text.lower()


def test_post_api_json_valid(client: TestClient):
    response = client.post(
        "/api/preferences",
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
    assert body["preferences"]["location"] == "Bangalore"
    assert "recommendations" in body
    assert body["source"] in ("groq", "fallback")


def test_post_api_json_invalid(client: TestClient):
    response = client.post(
        "/api/preferences",
        json={
            "location": "Delhi",
            "budget": "low",
            "cuisines": ["Chinese"],
        },
    )
    assert response.status_code == 422
    assert response.json()["ok"] is False
