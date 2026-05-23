"""
Phase 2 — preference validation and form/POST handlers.

Used by the basic web UI in ``zm.web``.
"""

from zm.input.schemas import (
    PreferenceErrorResponse,
    PreferenceFormInput,
    PreferenceJsonInput,
    PreferenceValidationResponse,
)
from zm.input.validator import validate_form, validate_json, validate_preferences

__all__ = [
    "PreferenceFormInput",
    "PreferenceJsonInput",
    "PreferenceValidationResponse",
    "PreferenceErrorResponse",
    "validate_preferences",
    "validate_form",
    "validate_json",
]
