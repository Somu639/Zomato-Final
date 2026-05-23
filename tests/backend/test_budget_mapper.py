from backend.services.budget_mapper import inr_for_two_to_band
from zm.models.enums import BudgetBand


def test_inr_low():
    assert inr_for_two_to_band(500) == BudgetBand.LOW


def test_inr_medium():
    assert inr_for_two_to_band(1500) == BudgetBand.MEDIUM


def test_inr_high():
    assert inr_for_two_to_band(3000) == BudgetBand.HIGH
