"""CLI entrypoint — developer tooling only (not end-user input).

End users submit preferences via the basic web UI (``zm.web``, Phase 2+).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from zm import __version__
from zm.config import get_settings
from zm.data import build_repository, get_repository_holder
from zm.exceptions import ConfigurationError, DataLoadError, ValidationError
from zm.models import BudgetBand, UserPreferences

PHASES = [
    ("0", "foundation", "active"),
    ("1", "data", "active"),
    ("2", "input", "active"),
    ("3", "integration", "active"),
    ("4", "engine", "active"),
    ("5a", "backend API", "active"),
    ("5b", "frontend SPA", "active"),
    ("6", "hardening", "active"),
    ("7", "streamlit deploy", "active"),
]


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )


def _ensure_repository(*, force_refresh: bool = False) -> "RestaurantRepository":
    """Load repository from cache/disk if not already in memory."""
    from zm.data.repository import RestaurantRepository

    holder = get_repository_holder()
    if not force_refresh and holder.repository and holder.repository.is_ready():
        return holder.repository

    settings = get_settings()
    settings.ensure_cache_dir()
    repo = build_repository(settings, force_refresh=force_refresh)
    holder.set(repo)
    return repo


def cmd_check() -> int:
    """Validate configuration and print phase status."""
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger("zm")

    try:
        cache_path = settings.ensure_cache_dir()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    summary = settings.redacted_summary()
    summary["dataset_cache_dir"] = str(cache_path)
    logger.debug("Active settings: %s", summary)

    print(f"ZM Restaurant Recommendation v{__version__}")
    print(f"Cache directory: {cache_path} (writable)")
    print(f"Groq configured: {settings.has_groq_api_key}")
    print(f"Dataset: {settings.hf_dataset_id}")
    print(f"API / interim UI: http://{settings.web_host}:{settings.web_port}")
    print("  `zm api` — REST backend (Phase 5a)")
    print("  `zm serve` — interim Jinja UI (legacy)")
    print("  Frontend: `cd frontend && npm run dev` (Phase 6 Next.js, :3000)")
    print("  Streamlit: `zm streamlit` (Phase 7, :8501)")
    print("Input channel: React SPA + REST API (CLI is dev-only)")

    from zm.data.cache import cache_paths, load_cache

    cache_path = settings.ensure_cache_dir()
    data_file, meta_file = cache_paths(cache_path)
    if data_file.is_file():
        cached, meta = load_cache(cache_path)
        count = len(cached)
        print(f"Data cache: {count} restaurants at {data_file}")
        if meta:
            print(f"  Generated: {meta.generated_at}")
    else:
        print("Data cache: none (run `zm load-data`)")

    print()
    print("Phases:")
    for number, name, status in PHASES:
        marker = "[x]" if status == "active" else "[ ]"
        print(f"  {marker} Phase {number} - {name} ({status})")

    if not settings.has_groq_api_key:
        print()
        print(
            "Note: GROQ_API_KEY is not set. Recommendations use rule-based fallback."
        )

    return 0


def cmd_load_data(*, force: bool = False) -> int:
    """Download, normalize, cache, and load the restaurant repository."""
    settings = get_settings()
    _configure_logging(settings.log_level)

    try:
        get_settings().ensure_cache_dir()
        repo = _ensure_repository(force_refresh=force)
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    locations = repo.get_known_locations()
    print(f"Loaded {repo.count()} restaurants into memory")
    print(f"Cities ({len(locations)}): {', '.join(locations)}")
    sample = repo.filter_by_location(locations[0])[:3] if locations else []
    if sample:
        print("Sample:")
        for rest in sample:
            rating = rest.rating if rest.rating is not None else "N/A"
            print(f"  - {rest.name} ({rest.cuisines[0]}…) rating={rating}")
    return 0


def cmd_data_stats() -> int:
    """Show repository stats (loads from cache if needed)."""
    _configure_logging(get_settings().log_level)
    try:
        repo = _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    locations = repo.get_known_locations()
    print(f"Restaurants: {repo.count()}")
    for city in locations:
        print(f"  {city}: {len(repo.filter_by_location(city))}")
    return 0


def cmd_candidates(
    *,
    location: str,
    budget: str,
    cuisines: str,
    min_rating: float,
    additional: str | None,
    json_output: bool,
) -> int:
    """Run Phase 3 filters and print candidate set (dev tooling)."""
    _configure_logging(get_settings().log_level)
    try:
        repo = _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    from zm.input.validator import validate_form
    from zm.integration import run_integration

    try:
        prefs = validate_form(
            {
                "location": location,
                "budget": budget,
                "cuisines": cuisines,
                "min_rating": str(min_rating),
                "additional": additional or "",
            },
            known_locations=repo.get_known_locations(),
        )
    except ValidationError as exc:
        print(f"Validation error: {exc.field_errors or exc}", file=sys.stderr)
        return 1

    result = run_integration(prefs, repo)
    if json_output:
        payload = {
            "candidate_count": len(result.candidates),
            "no_match_message": result.no_match_message,
            "filter_stats": result.filter_stats.__dict__,
            "candidates": [r.model_dump() for r in result.candidates[:10]],
            "context_bytes": len(result.context_json),
            "prompt_version": result.prompt_version,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0 if result.has_candidates else 1

    if not result.has_candidates:
        print(result.no_match_message or "No candidates", file=sys.stderr)
        return 1

    print(f"Candidates: {len(result.candidates)}")
    print(f"Filter funnel: {result.filter_stats}")
    for rest in result.candidates[:10]:
        rating = rest.rating if rest.rating is not None else "N/A"
        print(f"  - {rest.name} ({', '.join(rest.cuisines[:2])}) rating={rating}")
    print(f"Context JSON size: {len(result.context_json)} chars")
    return 0


def cmd_recommend(
    *,
    location: str,
    budget: str,
    cuisines: str,
    min_rating: float,
    additional: str | None,
    json_output: bool,
) -> int:
    """Full pipeline: validate → filter → Groq recommend."""
    _configure_logging(get_settings().log_level)
    try:
        repo = _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    from zm.engine import recommend
    from zm.input.validator import validate_form

    try:
        prefs = validate_form(
            {
                "location": location,
                "budget": budget,
                "cuisines": cuisines,
                "min_rating": str(min_rating),
                "additional": additional or "",
            },
            known_locations=repo.get_known_locations(),
        )
        engine = recommend(prefs, repo)
    except ValidationError as exc:
        print(f"Validation error: {exc.field_errors or exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if json_output:
        print(
            json.dumps(
                {
                    "source": engine.source,
                    "warning": engine.warning,
                    "summary": engine.result.summary,
                    "recommendations": [d.model_dump() for d in engine.displays],
                },
                indent=2,
                default=str,
            )
        )
        return 0

    if engine.warning:
        print(f"Warning: {engine.warning}")
    if engine.result.summary:
        print(engine.result.summary)
    for item in engine.displays:
        rating = item.rating if item.rating is not None else "N/A"
        print(
            f"#{item.rank} {item.name} ({rating}) — {item.estimated_cost}\n"
            f"   {item.explanation}"
        )
    print(f"Source: {engine.source}")
    return 0


def _ensure_project_root_on_path() -> None:
    """Allow ``import backend`` when running the editable ``zm`` CLI."""
    root = Path(__file__).resolve().parents[2]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def cmd_api() -> int:
    """Start the REST API backend (Phase 5a)."""
    _ensure_project_root_on_path()
    settings = get_settings()
    _configure_logging(settings.log_level)

    try:
        settings.ensure_cache_dir()
        _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        print("API will return 503 until data is loaded.", file=sys.stderr)

    from backend.main import run_server

    print(
        f"Starting API at http://{settings.web_host}:{settings.web_port}/"
    )
    print(f"OpenAPI docs: http://{settings.web_host}:{settings.web_port}/docs")
    print(f"CORS origins: {', '.join(settings.cors_origins_list)}")
    run_server()
    return 0


def cmd_streamlit() -> int:
    """Start the Streamlit deployment UI (Phase 7)."""
    import subprocess

    _ensure_project_root_on_path()
    settings = get_settings()
    _configure_logging(settings.log_level)

    try:
        settings.ensure_cache_dir()
        _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Warning: {exc}", file=sys.stderr)

    root = Path(__file__).resolve().parents[2]
    app_path = root / "streamlit_app" / "app.py"
    if not app_path.is_file():
        print(f"Error: Streamlit app not found at {app_path}", file=sys.stderr)
        return 1

    print("Starting Streamlit at http://localhost:8501/")
    print(f"App: {app_path}")
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        cwd=str(root),
    )


def cmd_serve() -> int:
    """Start the interim Jinja web UI (legacy)."""
    settings = get_settings()
    _configure_logging(settings.log_level)

    try:
        settings.ensure_cache_dir()
        _ensure_repository()
    except (ConfigurationError, DataLoadError) as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        print("The form will stay disabled until data is loaded.", file=sys.stderr)

    from zm.web import run_server

    print(
        f"Starting web UI at http://{settings.web_host}:{settings.web_port}/"
    )
    run_server(settings)
    return 0


def cmd_demo_models() -> int:
    """Serialize sample domain models (verifies contracts)."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisines=["Italian", "Chinese"],
        min_rating=4.0,
        additional="family-friendly",
    )
    print(json.dumps(prefs.model_dump(), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AI-powered restaurant recommendation (Zomato use case)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("check", help="Validate config and show phase status (default)")
    sub.add_parser("demo-models", help="Print sample UserPreferences JSON")

    load_parser = sub.add_parser(
        "load-data",
        help="Ingest Hugging Face dataset into cache and memory",
    )
    load_parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and rebuild cache",
    )

    sub.add_parser("data-stats", help="Show loaded restaurant counts by city")
    sub.add_parser("api", help="Start REST API backend (Phase 5a)")
    sub.add_parser("streamlit", help="Start Streamlit UI (Phase 7)")
    sub.add_parser("serve", help="Start interim Jinja web UI (legacy)")

    cand = sub.add_parser(
        "candidates",
        help="Run Phase 3 filters and show candidate set (dev)",
    )
    cand.add_argument("-l", "--location", required=True)
    cand.add_argument("-b", "--budget", required=True, choices=["low", "medium", "high"])
    cand.add_argument("-c", "--cuisines", required=True, help="Comma-separated cuisines")
    cand.add_argument("-r", "--min-rating", type=float, default=0.0)
    cand.add_argument("-a", "--additional", default=None)
    cand.add_argument("--json", action="store_true", dest="json_output")

    rec = sub.add_parser(
        "recommend",
        help="Full pipeline: preferences → Groq recommendations",
    )
    rec.add_argument("-l", "--location", required=True)
    rec.add_argument("-b", "--budget", required=True, choices=["low", "medium", "high"])
    rec.add_argument("-c", "--cuisines", required=True)
    rec.add_argument("-r", "--min-rating", type=float, default=0.0)
    rec.add_argument("-a", "--additional", default=None)
    rec.add_argument("--json", action="store_true", dest="json_output")

    args = parser.parse_args(argv)
    command = args.command or "check"

    if command == "check":
        return cmd_check()
    if command == "demo-models":
        return cmd_demo_models()
    if command == "load-data":
        return cmd_load_data(force=args.force)
    if command == "data-stats":
        return cmd_data_stats()
    if command == "api":
        return cmd_api()
    if command == "streamlit":
        return cmd_streamlit()
    if command == "serve":
        return cmd_serve()
    if command == "candidates":
        return cmd_candidates(
            location=args.location,
            budget=args.budget,
            cuisines=args.cuisines,
            min_rating=args.min_rating,
            additional=args.additional,
            json_output=args.json_output,
        )
    if command == "recommend":
        return cmd_recommend(
            location=args.location,
            budget=args.budget,
            cuisines=args.cuisines,
            min_rating=args.min_rating,
            additional=args.additional,
            json_output=args.json_output,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
