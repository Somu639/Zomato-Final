"""
Phase 3 — integration layer (separate package per architecture).

Filter restaurants, rank candidates, build LLM context and prompt v1.
"""

from zm.integration.context import build_llm_context, build_llm_context_json
from zm.integration.pipeline import (
    build_candidate_set,
    build_candidate_set_from_repo,
    build_no_match_message,
    run_integration,
)
from zm.integration.prompts import PROMPT_VERSION, build_prompts
from zm.integration.types import FilterStats, IntegrationResult

__all__ = [
    "FilterStats",
    "IntegrationResult",
    "build_candidate_set",
    "build_candidate_set_from_repo",
    "build_no_match_message",
    "build_llm_context",
    "build_llm_context_json",
    "build_prompts",
    "run_integration",
    "PROMPT_VERSION",
]
