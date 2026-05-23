"""Prompt template v1 for Phase 4 LLM (built in Phase 3)."""

from __future__ import annotations

from typing import Any

from zm.models import UserPreferences

PROMPT_VERSION = "v1"

SYSTEM_PROMPT_V1 = """You are a restaurant recommendation assistant for a Zomato-style dining app.

You receive:
1) Structured user preferences (location, budget, cuisines, minimum rating, optional notes).
2) A JSON list of candidate restaurants that already passed hard filters.

Your task:
- Rank ONLY restaurants present in the candidate list by fit to the user preferences.
- Use each candidate's ``restaurant_id`` exactly as given — never invent IDs.
- Explain why each pick matches location, budget, cuisine, rating, and any additional notes.
- Return valid JSON only, matching the schema provided in the user message.
"""

USER_PROMPT_TEMPLATE_V1 = """User preferences:
- Location: {location}
- Budget: {budget}
- Preferred cuisines: {cuisines}
- Minimum rating: {min_rating}
- Additional notes: {additional}

Candidate restaurants (JSON):
{context_json}

Return JSON with this shape:
{{
  "summary": "optional one-line overview",
  "recommendations": [
    {{
      "restaurant_id": "id from candidates",
      "rank": 1,
      "explanation": "why this matches the user preferences"
    }}
  ]
}}

Rank up to {display_top_n} restaurants. Only use restaurant_id values from the candidates list."""


def build_prompts(
    preferences: UserPreferences,
    context_json: str,
    *,
    display_top_n: int = 5,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for Phase 4."""
    additional = preferences.additional or "(none)"
    cuisines = ", ".join(preferences.cuisines)
    user_prompt = USER_PROMPT_TEMPLATE_V1.format(
        location=preferences.location,
        budget=preferences.budget.value,
        cuisines=cuisines,
        min_rating=preferences.min_rating,
        additional=additional,
        context_json=context_json,
        display_top_n=display_top_n,
    )
    return SYSTEM_PROMPT_V1, user_prompt


def build_prompt_payload(
    preferences: UserPreferences,
    context: dict[str, Any],
    context_json: str,
    *,
    display_top_n: int = 5,
) -> dict[str, Any]:
    """Full prompt package for debugging and Phase 4 handoff."""
    system_prompt, user_prompt = build_prompts(
        preferences,
        context_json,
        display_top_n=display_top_n,
    )
    return {
        "version": PROMPT_VERSION,
        "system": system_prompt,
        "user": user_prompt,
        "context": context,
    }
