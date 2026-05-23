"""Location matching against known cities from the dataset."""

from __future__ import annotations

import difflib


def match_known_location(
    user_input: str,
    known_locations: list[str],
) -> tuple[str | None, str | None]:
    """
    Resolve user location to a canonical city name.

    Returns:
        (canonical_location, error_message) — one of the two is set.
    """
    cleaned = user_input.strip()
    if not cleaned:
        return None, "location is required"

    if not known_locations:
        return cleaned, None

    by_key = {loc.casefold(): loc for loc in known_locations}
    key = cleaned.casefold()
    if key in by_key:
        return by_key[key], None

    suggestions = difflib.get_close_matches(
        cleaned,
        known_locations,
        n=1,
        cutoff=0.6,
    )
    if suggestions:
        return None, f"Did you mean {suggestions[0]}?"

    available = ", ".join(known_locations)
    return None, f"No coverage for '{cleaned}'. Available locations: {available}"
