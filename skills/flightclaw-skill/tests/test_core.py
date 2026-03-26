from datetime import date

from flightclaw.core.search import parse_date, today_payload
from flightclaw.providers.example import ExampleProvider


def test_parse_date():
    assert parse_date("2026-04-01") == date(2026, 4, 1)


def test_today_payload_shape():
    d = today_payload()
    assert "today" in d


def test_example_provider():
    p = ExampleProvider()
    r = p.search("BJS", "SHA", date(2026, 4, 1))
    assert r.to_json_dict()["provider"] == "example"
