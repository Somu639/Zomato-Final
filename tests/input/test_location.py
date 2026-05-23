from zm.input.location import match_known_location


def test_exact_match_case_insensitive():
    loc, err = match_known_location("bangalore", ["Bangalore", "Delhi"])
    assert loc == "Bangalore"
    assert err is None


def test_typo_suggests_close_match():
    loc, err = match_known_location("Banglore", ["Bangalore"])
    assert loc is None
    assert err is not None
    assert "Bangalore" in err


def test_unknown_location_lists_available():
    loc, err = match_known_location("Mumbai", ["Bangalore"])
    assert loc is None
    assert "No coverage" in (err or "")
