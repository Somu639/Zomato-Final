"""Shared enumerations for domain models."""

from enum import StrEnum


class BudgetBand(StrEnum):
    """User budget preference."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PriceBand(StrEnum):
    """Restaurant price band derived from cost data."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"
