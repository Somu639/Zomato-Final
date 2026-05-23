"""FastAPI application for the basic web UI (Phase 2)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from zm.config import Settings
from zm.exceptions import ValidationError
from zm.input.schemas import (
    PreferenceErrorResponse,
    PreferenceJsonInput,
    PreferenceValidationResponse,
)
from zm.input.validator import validate_form, validate_json
from zm.engine import recommend
from zm.engine.types import EngineResult
from zm.models import UserPreferences
from zm.web.deps import get_app_settings, get_restaurant_repository

logger = logging.getLogger(__name__)

WEB_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=WEB_DIR / "templates")


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_app_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        get_restaurant_repository()
        logger.info("Restaurant repository ready for web UI")
    except RuntimeError as exc:
        logger.warning("Startup: %s", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ZM Restaurant Recommendation",
        description="Phase 2 — preference form and validation",
        version="0.1.0",
        lifespan=_lifespan,
    )

    static_dir = WEB_DIR / "static"
    if static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def preference_form(
        request: Request,
        settings: Settings = Depends(get_app_settings),
    ) -> HTMLResponse:
        locations: list[str] = []
        data_ready = False
        load_error: str | None = None

        try:
            repo = get_restaurant_repository()
            locations = repo.get_known_locations()
            data_ready = bool(locations)
        except RuntimeError as exc:
            load_error = str(exc)

        return TEMPLATES.TemplateResponse(
            request,
            "index.html",
            {
                "title": "Find restaurants",
                "locations": locations,
                "data_ready": data_ready,
                "load_error": load_error,
                "budgets": ["low", "medium", "high"],
                "form": {},
                "errors": {},
                "success": None,
                "preferences": None,
                "integration": None,
                "recommendations": None,
            },
        )

    @app.post("/recommendations", response_class=HTMLResponse)
    async def submit_preferences_form(
        request: Request,
        location: str = Form(""),
        budget: str = Form(""),
        cuisines: str = Form(""),
        min_rating: str = Form("0"),
        additional: str = Form(""),
    ) -> HTMLResponse:
        try:
            repo = get_restaurant_repository()
        except RuntimeError as exc:
            return _form_template(
                request,
                form={
                    "location": location,
                    "budget": budget,
                    "cuisines": cuisines,
                    "min_rating": min_rating,
                    "additional": additional,
                },
                errors={"location": str(exc)},
                locations=[],
                data_ready=False,
                load_error=str(exc),
            )

        locations = repo.get_known_locations()
        form_data = {
            "location": location,
            "budget": budget,
            "cuisines": cuisines,
            "min_rating": min_rating,
            "additional": additional,
        }

        try:
            prefs = validate_form(form_data, known_locations=locations)
        except ValidationError as exc:
            return _form_template(
                request,
                form=form_data,
                errors=exc.field_errors,
                locations=locations,
                data_ready=True,
            )

        settings = get_app_settings()
        try:
            engine = recommend(prefs, repo, settings=settings)
        except ValueError as exc:
            return _form_template(
                request,
                form=form_data,
                errors={"_form": str(exc)},
                locations=locations,
                data_ready=True,
                preferences=prefs,
            )

        source_label = "Groq AI" if engine.source == "groq" else "rule-based"
        success = f"Top {len(engine.displays)} recommendations ({source_label})."

        return _form_template(
            request,
            form=form_data,
            errors={},
            locations=locations,
            data_ready=True,
            success=success,
            preferences=prefs,
            recommendations=_engine_payload(engine),
        )

    @app.post("/api/preferences")
    async def submit_preferences_json(
        body: PreferenceJsonInput,
    ) -> JSONResponse:
        try:
            repo = get_restaurant_repository()
        except RuntimeError as exc:
            return JSONResponse(
                status_code=503,
                content=PreferenceErrorResponse(
                    errors={"location": str(exc)},
                    message=str(exc),
                ).model_dump(),
            )

        try:
            prefs = validate_json(
                body.model_dump(),
                known_locations=repo.get_known_locations(),
            )
        except ValidationError as exc:
            return JSONResponse(
                status_code=422,
                content=PreferenceErrorResponse(
                    errors=exc.field_errors,
                ).model_dump(),
            )

        settings = get_app_settings()
        try:
            engine = recommend(prefs, repo, settings=settings)
        except ValueError as exc:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "message": str(exc),
                    "preferences": _preferences_payload(prefs),
                },
            )

        payload = _engine_payload(engine)
        return JSONResponse(
            content={
                "ok": True,
                "message": "Recommendations generated.",
                "preferences": _preferences_payload(prefs),
                "source": engine.source,
                "warning": engine.warning,
                **payload,
            },
        )

    return app


def _preferences_payload(prefs: UserPreferences) -> dict[str, object]:
    data = prefs.model_dump()
    data["budget"] = prefs.budget.value
    return data


def _engine_payload(engine: EngineResult) -> dict[str, object]:
    return {
        "summary": engine.result.summary,
        "source": engine.source,
        "warning": engine.warning,
        "recommendations": [item.model_dump() for item in engine.displays],
    }


def _form_template(
    request: Request,
    *,
    form: dict[str, str],
    errors: dict[str, str],
    locations: list[str],
    data_ready: bool,
    load_error: str | None = None,
    success: str | None = None,
    preferences: UserPreferences | None = None,
    integration: dict[str, object] | None = None,
    recommendations: dict[str, object] | None = None,
) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Find restaurants",
            "locations": locations,
            "data_ready": data_ready,
            "load_error": load_error,
            "budgets": ["low", "medium", "high"],
            "form": form,
            "errors": errors,
            "success": success,
            "preferences": _preferences_payload(preferences) if preferences else None,
            "integration": integration,
            "recommendations": recommendations,
        },
    )


def run_server(settings: Settings | None = None) -> None:
    """Run uvicorn (called from ``zm serve``)."""
    import uvicorn

    settings = settings or get_app_settings()
    uvicorn.run(
        "zm.web.app:create_app",
        factory=True,
        host=settings.web_host,
        port=settings.web_port,
        log_level=settings.log_level.lower(),
    )
