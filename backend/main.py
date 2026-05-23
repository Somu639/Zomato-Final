"""FastAPI REST API entry (Phase 5a / 6 / 7)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from backend.api.routes.discovery import router as discovery_router
from backend.api.routes.health import router as health_router
from backend.api.routes.recommendations import (
    register_exception_handlers,
    router as recommendations_router,
)
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.request_id import RequestIdFilter, RequestIdMiddleware
from backend.startup import bootstrap_repository, log_deployment_context
from zm.config import get_settings

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s %(name)s [%(request_id)s]: %(message)s",
    )
    for handler in logging.root.handlers:
        handler.addFilter(RequestIdFilter())


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    _configure_logging(settings.log_level)
    log_deployment_context(settings)
    bootstrap_repository(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ZM Restaurant Recommendation API",
        description="Phase 5a/6 — REST API for Next.js frontend",
        version="0.2.0",
        lifespan=lifespan,
    )

    if settings.is_render:
        app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
    )
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router)
    app.include_router(discovery_router)
    app.include_router(recommendations_router)
    register_exception_handlers(app)
    _register_not_found_handler(app)

    return app


def _register_not_found_handler(app: FastAPI) -> None:
    @app.exception_handler(404)
    async def not_found_handler(request: Request, _exc: Exception) -> JSONResponse:
        path = request.url.path
        hint = (
            "Use the REST API at /api/v1/... (see /docs). "
            "On Render, start command must be: "
            "bash scripts/render_start.sh — not zm serve (legacy UI)."
        )
        if path.startswith("/api/v1"):
            hint = "Check the path and HTTP method in /docs."
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "detail": "Not Found",
                "path": path,
                "message": hint,
                "try": {
                    "health": "/health",
                    "locations": "/api/v1/locations",
                    "docs": "/docs",
                },
            },
        )


def run_server() -> None:
    """Run uvicorn (``zm api``)."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:create_app",
        factory=True,
        host=settings.web_host,
        port=settings.web_port,
        log_level=settings.log_level.lower(),
        proxy_headers=settings.is_render,
        forwarded_allow_ips="*" if settings.is_render else None,
    )


app = create_app()
