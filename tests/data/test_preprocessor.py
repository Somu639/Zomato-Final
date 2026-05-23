from zm.data.preprocessor import dedupe_restaurants
from zm.models import Restaurant
from zm.models.enums import PriceBand


def _restaurant(name: str, rating: float | None, address: str = "Addr, Bangalore") -> Restaurant:
    return Restaurant(
        id=f"id-{name}",
        name=name,
        location="Bangalore",
        cuisines=["Indian"],
        rating=rating,
        price_band=PriceBand.MEDIUM,
        attributes={"address": address},
    )


def test_dedupe_keeps_higher_rating():
    a = _restaurant("Dup", 3.5, "Same, Bangalore")
    b = _restaurant("Dup", 4.2, "Same, Bangalore")
    result, removed = dedupe_restaurants([a, b])
    assert removed == 1
    assert len(result) == 1
    assert result[0].rating == 4.2
