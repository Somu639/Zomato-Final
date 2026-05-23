import json

from zm.engine.parser import parse_llm_response


def test_parse_llm_response_strips_fences():
    raw = """```json
{"summary": "Great picks", "recommendations": [
  {"restaurant_id": "a", "rank": 1, "explanation": "Italian fit"}
]}
```"""
    result = parse_llm_response(raw, allowed_ids={"a", "b"})
    assert result is not None
    assert result.summary == "Great picks"
    assert len(result.recommendations) == 1


def test_parse_skips_hallucinated_ids():
    raw = json.dumps(
        {
            "recommendations": [
                {"restaurant_id": "fake", "rank": 1, "explanation": "nope"},
                {"restaurant_id": "real", "rank": 2, "explanation": "yes"},
            ]
        }
    )
    result = parse_llm_response(raw, allowed_ids={"real"})
    assert result is not None
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "real"
    assert result.recommendations[0].rank == 1
