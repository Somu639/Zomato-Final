"""Parse Groq LLM JSON completions into ``RecommendationResult``."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from zm.models import Recommendation, RecommendationResult

logger = logging.getLogger(__name__)

_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


class _RawRecommendation(BaseModel):
    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str = Field(min_length=1)


class _RawLLMResponse(BaseModel):
    summary: str | None = None
    recommendations: list[_RawRecommendation] = Field(min_length=1)


def _strip_markdown_fences(text: str) -> str:
    match = _FENCE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _try_parse_json(text: str) -> dict[str, Any] | None:
    cleaned = _strip_markdown_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


def parse_llm_response(
    raw_text: str,
    *,
    allowed_ids: set[str],
    max_items: int | None = None,
) -> RecommendationResult | None:
    """
    Parse LLM output and keep only recommendations with valid ``restaurant_id``.

    Returns ``None`` if parsing fails or no valid items remain (P4-08–P4-17).
    """
    payload = _try_parse_json(raw_text)
    if payload is None:
        logger.warning("LLM response is not valid JSON")
        return None

    try:
        parsed = _RawLLMResponse.model_validate(payload)
    except PydanticValidationError as exc:
        logger.warning("LLM JSON schema validation failed: %s", exc)
        return None

    valid: list[Recommendation] = []
    for item in sorted(parsed.recommendations, key=lambda x: x.rank):
        if item.restaurant_id not in allowed_ids:
            logger.warning("Skipping hallucinated restaurant_id: %s", item.restaurant_id)
            continue
        valid.append(
            Recommendation(
                restaurant_id=item.restaurant_id,
                rank=item.rank,
                explanation=item.explanation,
            )
        )

    if not valid:
        return None

    if max_items is not None:
        valid = valid[:max_items]

    # Renumber ranks after filtering
    renumbered = [
        Recommendation(
            restaurant_id=item.restaurant_id,
            rank=index + 1,
            explanation=item.explanation,
        )
        for index, item in enumerate(valid)
    ]

    return RecommendationResult(
        recommendations=renumbered,
        summary=parsed.summary,
    )
