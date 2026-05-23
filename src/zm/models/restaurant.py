"""Restaurant domain model (Phase 0 contract for Phase 1 ingestion)."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from zm.models.enums import PriceBand


class Restaurant(BaseModel):
    """Normalized restaurant record from the dataset."""

    id: str = Field(min_length=1, description="Stable identifier")
    name: str = Field(min_length=1)
    location: str = Field(min_length=1, description="City or normalized area")
    cuisines: list[str] = Field(min_length=1)
    cost_for_two: int | None = Field(
        default=None,
        ge=0,
        description="Approximate cost for two in local currency units",
    )
    price_band: PriceBand = PriceBand.UNKNOWN
    rating: float | None = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="Aggregate rating; null if unknown or NEW",
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra dataset fields (delivery, dine-in, etc.)",
    )

    @field_validator("cuisines", mode="before")
    @classmethod
    def normalize_cuisines(cls, value: object) -> list[str]:
        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",") if part.strip()]
            if not parts:
                raise ValueError("At least one cuisine is required")
            return parts
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            if not cleaned:
                raise ValueError("At least one cuisine is required")
            return cleaned
        raise ValueError("cuisines must be a string or list of strings")

    model_config = {"frozen": True, "extra": "forbid"}
