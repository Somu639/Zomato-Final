"""FastAPI REST API entry (Phase 5a / 6)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.deps import get_restaurant_repository
from backend.api.routes.health import router as health_router
from backend.api.routes.recommendations import (
    register_exception_handlers,
    router as recommendations_router,
)
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.request_id import RequestIdFilter, RequestIdMiddleware
from zm.config import get_settings
from zm.exceptions import DataLoadError

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
    try:
        repo = get_restaurant_repository()
        logger.info("Restaurant repository ready (%s restaurants)", repo.count())
    except DataLoadError as exc:
        logger.warning("Startup: %s", exc)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ZM Restaurant Recommendation API",
        description="Phase 5a/6 — REST API for Next.js frontend",
        version="0.2.0",
        lifespan=lifespan,
    )

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
    app.include_router(recommendations_router)
    register_exception_handlers(app)

    return app


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
    )


app = create_app()
