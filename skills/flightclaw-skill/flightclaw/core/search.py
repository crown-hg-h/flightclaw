from __future__ import annotations

from datetime import date, datetime

from flightclaw.core.models import SearchQuery
from flightclaw.providers import get_provider


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def run_search(origin: str, destination: str, flight_date: str, provider: str) -> dict:
    p = get_provider(provider)
    d = parse_date(flight_date)
    result = p.search(origin, destination, d)
    return result.to_json_dict()


def today_payload() -> dict:
    from datetime import date as date_cls

    d = date_cls.today()
    return {"today": d.isoformat(), "local_timezone": "host machine local date"}
