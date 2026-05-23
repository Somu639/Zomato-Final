"""API discovery routes — avoid bare 404 on common paths (Render / ops)."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["discovery"])

_V1_ENDPOINTS = {
    "locations": "GET /api/v1/locations",
    "metadata": "GET /api/v1/metadata",
    "recommendations": "POST /api/v1/recommendations",
}


@router.get("/api", include_in_schema=False)
@router.get("/api/v1", include_in_schema=False)
def api_discovery() -> dict[str, object]:
    return {
        "service": "zm-restaurant-api",
        "version": "v1",
        "endpoints": _V1_ENDPOINTS,
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/locations", include_in_schema=False)
def locations_alias() -> RedirectResponse:
    return RedirectResponse(url="/api/v1/locations", status_code=307)
