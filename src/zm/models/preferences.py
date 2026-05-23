"""User preference model (Phase 0 contract for Phase 2 input)."""

from pydantic import BaseModel, Field, field_validator

from zm.models.enums import BudgetBand


class UserPreferences(BaseModel):
    """Validated user preferences for filtering and LLM context."""

    location: str = Field(min_length=1, description="City or area, e.g. Delhi")
    budget: BudgetBand
    cuisines: list[str] = Field(min_length=1)
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional: str | None = Field(
        default=None,
        max_length=500,
        description="Free-text extras: family-friendly, quick service, etc.",
    )

    @field_validator("location", "additional", mode="before")
    @classmethod
    def strip_strings(cls, value: object) -> object:
        if value is None:
            return value
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value

    @field_validator("location")
    @classmethod
    def location_not_blank(cls, value: str | None) -> str:
        if not value:
            raise ValueError("location is required")
        return value

    @staticmethod
    def _dedupe_cuisines(tokens: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for token in tokens:
            key = token.casefold()
            if key not in seen:
                seen.add(key)
                result.append(token)
        return result

    @field_validator("cuisines", mode="before")
    @classmethod
    def normalize_cuisines(cls, value: object) -> list[str]:
        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",") if part.strip()]
            if not parts:
                raise ValueError("At least one cuisine is required")
            return cls._dedupe_cuisines(parts)
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            result = cls._dedupe_cuisines(cleaned)
            if not result:
                raise ValueError("At least one cuisine is required")
            return result
        raise ValueError("cuisines must be a string or list of strings")

    @field_validator("budget", mode="before")
    @classmethod
    def normalize_budget(cls, value: object) -> BudgetBand:
        if isinstance(value, BudgetBand):
            return value
        if isinstance(value, str):
            normalized = value.strip().casefold()
            try:
                return BudgetBand(normalized)
            except ValueError as exc:
                allowed = ", ".join(b.value for b in BudgetBand)
                raise ValueError(
                    f"budget must be one of: {allowed}"
                ) from exc
        raise ValueError("budget must be a string")

    model_config = {"frozen": True, "extra": "forbid"}
