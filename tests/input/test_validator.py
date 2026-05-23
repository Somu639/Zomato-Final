import pytest

from zm.exceptions import ValidationError
from zm.input.validator import validate_form, validate_json
from zm.models.enums import BudgetBand


def test_validate_form_success():
    prefs = validate_form(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisines": "Italian, Chinese",
            "min_rating": "4.0",
            "additional": "family-friendly",
        },
        known_locations=["Bangalore"],
    )
    assert prefs.location == "Bangalore"
    assert prefs.budget == BudgetBand.MEDIUM
    assert prefs.cuisines == ["Italian", "Chinese"]
    assert prefs.min_rating == 4.0


def test_validate_form_rejects_missing_cuisine():
    with pytest.raises(ValidationError) as exc_info:
        validate_form(
            {
                "location": "Bangalore",
                "budget": "low",
                "cuisines": "",
            },
            known_locations=["Bangalore"],
        )
    assert "cuisines" in exc_info.value.field_errors


def test_validate_form_rejects_invalid_budget():
    with pytest.raises(ValidationError) as exc_info:
        validate_form(
            {
                "location": "Bangalore",
                "budget": "cheap",
                "cuisines": "Thai",
            },
            known_locations=["Bangalore"],
        )
    assert "budget" in exc_info.value.field_errors


def test_validate_json_accepts_cuisine_list():
    prefs = validate_json(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisines": ["North Indian", "Chinese"],
            "min_rating": 3.5,
        },
        known_locations=["Bangalore"],
    )
    assert len(prefs.cuisines) == 2


def test_validate_requires_loaded_locations():
    with pytest.raises(ValidationError) as exc_info:
        validate_form(
            {
                "location": "Bangalore",
                "budget": "low",
                "cuisines": "Thai",
            },
            known_locations=[],
        )
    assert "location" in exc_info.value.field_errors
