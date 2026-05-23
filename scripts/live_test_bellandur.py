"""Live Phase 4 test: Bellandur, ~2000 budget, min rating 4.0, top 5 via Groq."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Load GROQ_API_KEY from data/.env if present (user may store key there)
_data_env = Path(__file__).resolve().parents[1] / "data" / ".env"
if _data_env.is_file() and not os.environ.get("GROQ_API_KEY"):
    for line in _data_env.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("GROQ_API_KEY="):
            os.environ["GROQ_API_KEY"] = line.split("=", 1)[1].strip()
            break

from zm.config import get_settings
from zm.config.settings import Settings

get_settings.cache_clear()

from zm.data import build_repository
from zm.engine import run_recommendation
from zm.integration import build_candidate_set
from zm.integration.context import build_llm_context_json
from zm.integration.prompts import build_prompts
from zm.integration.types import IntegrationResult
from zm.models import UserPreferences


def main() -> int:
    settings = get_settings()
    if not settings.has_groq_api_key:
        print(
            "Note: GROQ_API_KEY not found on disk. Save data/.env or create .env at project root.",
            file=sys.stderr,
        )
        print("Continuing with rule-based fallback for demo.\n", file=sys.stderr)

    repo = build_repository(settings)

    # Bellandur is an area in Bangalore; city filter + area scope
    prefs = UserPreferences(
        location="Bangalore",
        budget="high",  # ~₹2000 for two maps to high price band
        cuisines="North Indian, Chinese, Italian, Cafe, Biryani",
        min_rating=4.0,
        additional=(
            "Prefer Bellandur area only. Budget approximately 2000 rupees for two people."
        ),
    )

    all_blr = repo.filter_by_location("Bangalore")
    bellandur = [
        r
        for r in all_blr
        if "bellandur" in str(r.attributes.get("area", "")).casefold()
    ]
    print(f"Input: Bellandur (area), budget ~2000, min rating 4.0")
    print(f"Bellandur-area restaurants in dataset: {len(bellandur)}")

    candidates, stats, no_match = build_candidate_set(
        prefs, bellandur, settings=settings
    )
    print(f"After filters (rating/cuisine/budget): {len(candidates)}")
    print(f"Filter funnel: {stats}")

    if no_match or not candidates:
        print(no_match or "No candidates after filtering")
        return 1

    context, context_json = build_llm_context_json(candidates, prefs)
    system_prompt, user_prompt = build_prompts(
        prefs, context_json, display_top_n=5
    )
    integration = IntegrationResult(
        preferences=prefs,
        candidates=candidates,
        context=context,
        context_json=context_json,
        prompt_version="v1",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        filter_stats=stats,
    )

    print("\nCalling Groq LLM...")
    engine = run_recommendation(integration, repo, settings=settings)
    print(f"Source: {engine.source}")
    if engine.warning:
        print(f"Warning: {engine.warning}")
    if engine.result.summary:
        print(f"Summary: {engine.result.summary}")

    print("\nTOP 5 RECOMMENDATIONS")
    print("=" * 60)
    for item in engine.displays[:5]:
        print(f"#{item.rank} {item.name}")
        print(f"   Cuisine: {', '.join(item.cuisines)}")
        cost = item.estimated_cost.replace("\u20b9", "Rs.")
        print(f"   Rating: {item.rating} | Cost: {cost}")
        print(f"   {item.explanation}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
