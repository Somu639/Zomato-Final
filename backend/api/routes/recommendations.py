"""Recommendation API routes (Phase 5a / 6)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from backend.api.deps import get_app_settings, get_restaurant_repository
from backend.api.schemas import ErrorResponse, RecommendationRequest, RecommendationResponse
from backend.cache import get_recommendation_cache
from backend.services.recommendation_service import NoMatchError, recommend
from zm.config import Settings
from zm.data.repository import RestaurantRepository
from zm.exceptions import DataLoadError, ValidationError

router = APIRouter(tags=["recommendations"])


@router.post(
    "/api/v1/recommendations",
    response_model=RecommendationResponse,
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    },
)
def create_recommendations(
    body: RecommendationRequest,
    response: Response,
    repo: RestaurantRepository = Depends(get_restaurant_repository),
    settings: Settings = Depends(get_app_settings),
) -> RecommendationResponse | JSONResponse:
    try:
        cache = get_recommendation_cache(settings.recommendation_cache_ttl_seconds)
        cache_key = cache.make_key(body.model_dump(mode="json"))
        cached = cache.get(cache_key)
        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            return cached.model_copy(update={"cached": True})

        result = recommend(body, repo, settings=settings)
        cache.set(cache_key, result)
        response.headers["X-Cache"] = "MISS"
        return result
    except PydanticValidationError as exc:
        errors = {
            ".".join(str(x) for x in err["loc"]): err["msg"]
            for err in exc.errors()
        }
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                errors=errors,
                message="Please fix the errors below.",
            ).model_dump(),
        )
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                errors=exc.field_errors,
                message="Please fix the errors below.",
            ).model_dump(),
        )
    except NoMatchError as exc:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                message=exc.message,
                errors={},
            ).model_dump(),
        )


def register_exception_handlers(app) -> None:
    @app.exception_handler(DataLoadError)
    async def data_load_error_handler(_request, exc: DataLoadError):
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                message=str(exc),
                errors={"_data": str(exc)},
            ).model_dump(),
        )
