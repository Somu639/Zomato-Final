from zm.data.normalizer import (
    cost_to_price_band,
    extract_city,
    normalize_row,
    parse_cost_for_two,
    parse_rating,
)
from zm.models.enums import PriceBand


def test_parse_rating_formats():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_cost_range():
    assert parse_cost_for_two("300-400") == 350
    assert parse_cost_for_two("800") == 800


def test_extract_city_from_address_and_url():
    assert extract_city("Foo, Bangalore", "") == "Bangalore"
    assert extract_city("", "https://www.zomato.com/delhi/place") == "Delhi"


def test_extract_city_rejects_unknown_url_slug():
    assert extract_city("", "https://www.zomato.com/cafe-remix?context=abc") is None


def test_normalize_row_success():
    row = {
        "url": "https://www.zomato.com/bangalore/jalsa",
        "address": "Banashankari, Bangalore",
        "name": "Jalsa",
        "cuisines": "North Indian, Chinese",
        "approx_cost(for two people)": "800",
        "rate": "4.1/5",
        "location": "Banashankari",
        "listed_in(city)": "Banashankari",
    }
    rest = normalize_row(row, row_index=0)
    assert rest is not None
    assert rest.name == "Jalsa"
    assert rest.location == "Bangalore"
    assert rest.price_band == PriceBand.HIGH
    assert rest.rating == 4.1


def test_normalize_row_skips_missing_name():
    assert normalize_row({"address": "Bangalore"}, row_index=0) is None


def test_cost_to_price_band():
    assert cost_to_price_band(200) == PriceBand.LOW
    assert cost_to_price_band(500) == PriceBand.MEDIUM
    assert cost_to_price_band(900) == PriceBand.HIGH
    assert cost_to_price_band(None) == PriceBand.UNKNOWN
