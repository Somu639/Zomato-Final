"""Raw input shapes from the web form and JSON API."""

from pydantic import BaseModel, Field


class PreferenceFormInput(BaseModel):
    """Unvalidated preference fields as submitted by the client."""

    location: str = ""
    budget: str = ""
    cuisines: str = ""
    min_rating: str = "0"
    additional: str | None = None

    model_config = {"extra": "ignore"}


class PreferenceJsonInput(BaseModel):
    """JSON body for ``POST /api/preferences``."""

    location: str
    budget: str
    cuisines: str | list[str]
    min_rating: float | str = 0.0
    additional: str | None = None

    model_config = {"extra": "ignore"}


class PreferenceValidationResponse(BaseModel):
    """Successful validation payload returned to the client."""

    ok: bool = True
    preferences: dict[str, object]
    message: str = "Preferences validated successfully."
    candidate_count: int | None = None
    candidate_preview: list[dict[str, object]] | None = None
    filter_stats: dict[str, int] | None = None
    no_match_message: str | None = None


class PreferenceErrorResponse(BaseModel):
    """Validation failure payload."""

    ok: bool = False
    errors: dict[str, str]
    message: str = "Please fix the errors below."
