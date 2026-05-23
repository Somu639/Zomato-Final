"""Map numeric INR budget (for two) to budget band (Phase 6)."""

from __future__ import annotations

from zm.models.enums import BudgetBand

# Typical Zomato "cost for two" bands (INR)
LOW_MAX = 600
MEDIUM_MAX = 2000


def inr_for_two_to_band(amount: int) -> BudgetBand:
    """Map rupee budget for two people to low | medium | high."""
    if amount <= LOW_MAX:
        return BudgetBand.LOW
    if amount <= MEDIUM_MAX:
        return BudgetBand.MEDIUM
    return BudgetBand.HIGH


def band_label(band: BudgetBand) -> str:
    return band.value
