"""Validate raw preference input into ``UserPreferences``."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from zm.exceptions import ValidationError
from zm.input.location import match_known_location
from zm.input.schemas import PreferenceFormInput, PreferenceJsonInput
from zm.models import UserPreferences
from zm.models.enums import BudgetBand


def _field_errors_from_pydantic(exc: PydanticValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for err in exc.errors():
        loc = err.get("loc", ())
        field = str(loc[-1]) if loc else "_form"
        msg = err.get("msg", "Invalid value")
        errors[field] = msg
    return errors


def _parse_min_rating(raw: str | float) -> tuple[float | None, str | None]:
    if isinstance(raw, (int, float)):
        value = float(raw)
    else:
        text = str(raw).strip()
        if not text:
            return 0.0, None
        try:
            value = float(text)
        except ValueError:
            return None, "min_rating must be a number"
    if value < 0 or value > 5:
        return None, "min_rating must be between 0 and 5"
    return value, None


def _sanitize_additional(text: str | None) -> str | None:
    if text is None:
        return None
    cleaned = text.strip()
    if not cleaned:
        return None
    if len(cleaned) > 500:
        return None  # signal error via validator
    return cleaned


def validate_preferences(
    data: dict[str, Any],
    *,
    known_locations: list[str],
    from_json: bool = False,
) -> UserPreferences:
    """
    Validate form or JSON payload and return ``UserPreferences``.

    Raises:
        ValidationError: With ``field_errors`` keyed by form field name.
    """
    field_errors: dict[str, str] = {}

    try:
        if from_json:
            parsed = PreferenceJsonInput.model_validate(data)
            location_raw = parsed.location
            budget_raw = parsed.budget
            cuisines_raw: str | list[str] = parsed.cuisines
            min_rating_raw: str | float = parsed.min_rating
            additional_raw = parsed.additional
        else:
            parsed = PreferenceFormInput.model_validate(data)
            location_raw = parsed.location
            budget_raw = parsed.budget
            cuisines_raw = parsed.cuisines
            min_rating_raw = parsed.min_rating
            additional_raw = parsed.additional
    except PydanticValidationError as exc:
        raise ValidationError(
            "Invalid preference payload",
            field_errors=_field_errors_from_pydantic(exc),
        ) from exc

    location, loc_err = match_known_location(location_raw, known_locations)
    if loc_err:
        field_errors["location"] = loc_err

    min_rating, rating_err = _parse_min_rating(min_rating_raw)
    if rating_err:
        field_errors["min_rating"] = rating_err

    additional = _sanitize_additional(additional_raw)
    if additional_raw and additional_raw.strip() and additional is None:
        field_errors["additional"] = "additional must be at most 500 characters"

    if field_errors:
        raise ValidationError("Validation failed", field_errors=field_errors)

    if not known_locations:
        field_errors["location"] = (
            "Restaurant data is not loaded. Run `zm load-data` first."
        )
        raise ValidationError("Validation failed", field_errors=field_errors)

    try:
        return UserPreferences(
            location=location or location_raw,
            budget=budget_raw,
            cuisines=cuisines_raw,
            min_rating=min_rating if min_rating is not None else 0.0,
            additional=additional,
        )
    except PydanticValidationError as exc:
        raise ValidationError(
            "Validation failed",
            field_errors=_field_errors_from_pydantic(exc),
        ) from exc


def validate_form(
    data: dict[str, Any],
    *,
    known_locations: list[str],
) -> UserPreferences:
    """Validate ``application/x-www-form-urlencoded`` or form fields."""
    return validate_preferences(data, known_locations=known_locations, from_json=False)


def validate_json(
    data: dict[str, Any],
    *,
    known_locations: list[str],
) -> UserPreferences:
    """Validate JSON API body."""
    return validate_preferences(data, known_locations=known_locations, from_json=True)
