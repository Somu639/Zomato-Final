"""
Phase 4 — recommendation engine using Groq.

Filter (Phase 3) → Groq LLM → parse → ``RecommendationResult`` with fallback.
"""

from zm.engine.groq_client import GroqLLMClient, create_groq_client
from zm.engine.parser import parse_llm_response
from zm.engine.pipeline import run_recommendation
from zm.engine.service import recommend
from zm.engine.types import EngineResult

__all__ = [
    "GroqLLMClient",
    "create_groq_client",
    "parse_llm_response",
    "run_recommendation",
    "recommend",
    "EngineResult",
]
