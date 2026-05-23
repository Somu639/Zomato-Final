"""Build compact LLM-ready context payloads."""

from __future__ import annotations

import json
from typing import Any

from zm.models import Restaurant, UserPreferences

# Rough guard for prompt size before Phase 4 token budgeting
DEFAULT_MAX_CONTEXT_CHARS = 12_000


def restaurant_to_context_row(restaurant: Restaurant) -> dict[str, Any]:
    """Minimal fields for LLM reasoning (P3 deterministic IDs)."""
    row: dict[str, Any] = {
        "restaurant_id": restaurant.id,
        "name": restaurant.name,
        "cuisines": restaurant.cuisines,
        "rating": restaurant.rating,
        "cost_for_two": restaurant.cost_for_two,
        "price_band": restaurant.price_band.value,
        "location": restaurant.location,
    }
    area = restaurant.attributes.get("area")
    if area:
        row["area"] = area
    rest_type = restaurant.attributes.get("rest_type")
    if rest_type:
        row["rest_type"] = rest_type
    return row


def build_llm_context(
    candidates: list[Restaurant],
    preferences: UserPreferences,
) -> dict[str, Any]:
    """Structured context dict for prompts and tests."""
    return {
        "user_preferences": {
            "location": preferences.location,
            "budget": preferences.budget.value,
            "cuisines": preferences.cuisines,
            "min_rating": preferences.min_rating,
            "additional": preferences.additional,
        },
        "candidates": [restaurant_to_context_row(r) for r in candidates],
        "candidate_count": len(candidates),
    }


def build_llm_context_json(
    candidates: list[Restaurant],
    preferences: UserPreferences,
    *,
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> tuple[dict[str, Any], str]:
    """
    Build context dict and JSON string, shrinking candidate list if needed (P3-14).
    """
    current = candidates
    while current:
        payload = build_llm_context(current, preferences)
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if len(text) <= max_chars:
            return payload, text
        # Drop lowest-ranked candidates (list is pre-sorted best-first)
        trim = max(1, len(current) // 5)
        current = current[:-trim]

    empty = build_llm_context([], preferences)
    return empty, json.dumps(empty, ensure_ascii=False, indent=2)
