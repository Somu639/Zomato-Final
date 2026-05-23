"""Map raw Zomato CSV rows to ``Restaurant`` models."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

from zm.data.constants import (
    CITY_ALIASES,
    COL_ADDRESS,
    COL_BOOK_TABLE,
    COL_COST,
    COL_CUISINES,
    COL_DISH_LIKED,
    COL_LISTED_IN_CITY,
    COL_LISTED_IN_TYPE,
    COL_LOCATION,
    COL_NAME,
    COL_ONLINE_ORDER,
    COL_PHONE,
    COL_RATE,
    COL_REST_TYPE,
    COL_URL,
    COL_VOTES,
    COST_BAND_LOW_MAX,
    COST_BAND_MEDIUM_MAX,
)
from zm.models import Restaurant
from zm.models.enums import PriceBand

logger = logging.getLogger(__name__)

_RATING_PATTERN = re.compile(r"(\d+(?:\.\d+)?)")
_COST_DIGITS = re.compile(r"\d+")
_NEW_RATINGS = frozenset({"new", "-", "na", "n/a", ""})


def _stable_id(name: str, city: str, address: str) -> str:
    payload = f"{name}|{city}|{address}".casefold().encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def extract_city(address: str, url: str = "") -> str | None:
    """Resolve canonical city from address text or Zomato URL path."""
    lower = address.casefold()
    for needle, canonical in sorted(CITY_ALIASES.items(), key=lambda item: -len(item[0])):
        if needle in lower:
            return canonical

    if url and "zomato.com/" in url.casefold():
        path = url.casefold().split("zomato.com/", 1)[1]
        first_segment = path.split("/", 1)[0].split("?", 1)[0]
        # Standard pattern: zomato.com/{city}/{restaurant}
        if first_segment in CITY_ALIASES:
            return CITY_ALIASES[first_segment]

    return None


def parse_rating(raw: str | None) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if text.casefold() in _NEW_RATINGS:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    match = _RATING_PATTERN.search(text)
    if not match:
        return None
    value = float(match.group(1))
    if value < 0 or value > 5:
        return None
    return value


def parse_cost_for_two(raw: str | None) -> int | None:
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "")
    if not text or text.casefold() in _NEW_RATINGS:
        return None
    numbers = [int(n) for n in _COST_DIGITS.findall(text)]
    if not numbers:
        return None
    # Ranges like "300-400" -> use midpoint-ish (average)
    value = sum(numbers) // len(numbers)
    if value < 0 or value > 999_999:
        return None
    return value


def cost_to_price_band(cost: int | None) -> PriceBand:
    if cost is None:
        return PriceBand.UNKNOWN
    if cost <= COST_BAND_LOW_MAX:
        return PriceBand.LOW
    if cost <= COST_BAND_MEDIUM_MAX:
        return PriceBand.MEDIUM
    return PriceBand.HIGH


def normalize_row(row: dict[str, Any], *, row_index: int) -> Restaurant | None:
    """
    Convert one CSV row to a ``Restaurant``, or ``None`` if the row should be skipped.
    """
    name = str(row.get(COL_NAME, "")).strip()
    address = str(row.get(COL_ADDRESS, "")).strip()
    url = str(row.get(COL_URL, "")).strip()

    if not name:
        logger.debug("Skipping row %s: missing name", row_index)
        return None

    city = extract_city(address, url)
    if not city:
        logger.debug("Skipping row %s: could not resolve city", row_index)
        return None

    cuisines_raw = str(row.get(COL_CUISINES, "")).strip()
    if not cuisines_raw:
        logger.debug("Skipping row %s: missing cuisines", row_index)
        return None

    cost = parse_cost_for_two(row.get(COL_COST))
    rating = parse_rating(row.get(COL_RATE))

    area = str(row.get(COL_LOCATION, "")).strip()
    listed_in = str(row.get(COL_LISTED_IN_CITY, "")).strip()

    attributes: dict[str, Any] = {
        "address": address,
        "area": area,
        "listed_in": listed_in,
        "url": url,
        "rest_type": str(row.get(COL_REST_TYPE, "")).strip() or None,
        "online_order": str(row.get(COL_ONLINE_ORDER, "")).strip() or None,
        "book_table": str(row.get(COL_BOOK_TABLE, "")).strip() or None,
        "votes": str(row.get(COL_VOTES, "")).strip() or None,
        "phone": str(row.get(COL_PHONE, "")).strip() or None,
        "dish_liked": str(row.get(COL_DISH_LIKED, "")).strip() or None,
        "listed_in_type": str(row.get(COL_LISTED_IN_TYPE, "")).strip() or None,
    }
    attributes = {key: value for key, value in attributes.items() if value is not None}

    return Restaurant(
        id=_stable_id(name, city, address),
        name=name,
        location=city,
        cuisines=cuisines_raw,
        cost_for_two=cost,
        price_band=cost_to_price_band(cost),
        rating=rating,
        attributes=attributes,
    )
