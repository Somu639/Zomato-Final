"""Recommendation engine pipeline (Phase 4)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from zm.config import Settings, get_settings
from zm.engine.enrich import enrich_recommendations
from zm.engine.fallback import fallback_recommendations
from zm.engine.groq_client import create_groq_client
from zm.engine.parser import parse_llm_response
from zm.engine.types import EngineResult
from zm.exceptions import ConfigurationError
from zm.integration.types import IntegrationResult

if TYPE_CHECKING:
    from zm.interfaces.data_source import RestaurantRepositoryPort

logger = logging.getLogger(__name__)


class LLMCompleter(Protocol):
    def complete(self, *, system_prompt: str, user_prompt: str) -> str: ...


def run_recommendation(
    integration: IntegrationResult,
    repository: RestaurantRepositoryPort,
    *,
    settings: Settings | None = None,
    client: LLMCompleter | None = None,
) -> EngineResult:
    """
    Run Groq LLM ranking on Phase 3 output, with rule-based fallback.

    Does not call the LLM when there are zero candidates (P3-15).
    """
    settings = settings or get_settings()

    if not integration.has_candidates:
        raise ValueError(integration.no_match_message or "No candidates to recommend")

    candidates_by_id = {r.id: r for r in integration.candidates}
    allowed_ids = set(candidates_by_id.keys())
    top_n = settings.display_top_n
    warning: str | None = None

    if settings.has_groq_api_key:
        try:
            groq = client or create_groq_client(settings)
            raw = groq.complete(
                system_prompt=integration.system_prompt,
                user_prompt=integration.user_prompt,
            )
            parsed = parse_llm_response(
                raw,
                allowed_ids=allowed_ids,
                max_items=top_n,
            )
            if parsed is not None:
                displays = enrich_recommendations(
                    parsed.recommendations,
                    candidates_by_id,
                )
                if displays:
                    logger.info(
                        "Groq recommendations: %s items", len(parsed.recommendations)
                    )
                    return EngineResult(
                        result=parsed,
                        displays=displays,
                        source="groq",
                    )
            warning = "AI response could not be parsed; using rule-based ranking."
            logger.warning(warning)
        except (ConfigurationError, RuntimeError) as exc:
            warning = f"AI explanations unavailable: {exc}"
            logger.warning(warning)
        except Exception as exc:
            warning = f"AI explanations unavailable: {exc}"
            logger.exception("Unexpected Groq error")
    else:
        warning = (
            "GROQ_API_KEY is not set. Showing rule-based recommendations only."
        )

    fallback = fallback_recommendations(
        integration.candidates,
        integration.preferences,
        top_n=top_n,
    )
    displays = enrich_recommendations(fallback.recommendations, candidates_by_id)
    return EngineResult(
        result=fallback,
        displays=displays,
        source="fallback",
        warning=warning,
    )
