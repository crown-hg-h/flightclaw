from __future__ import annotations

from datetime import date

from flightclaw.core.models import FlightOffer, SearchQuery, SearchResult
from flightclaw.providers.base import BaseProvider


class ExampleProvider(BaseProvider):
    """Mock provider for pipeline tests — does not hit the network."""

    name = "example"

    def search(self, origin: str, destination: str, flight_date: date) -> SearchResult:
        q = SearchQuery(origin=origin.upper(), destination=destination.upper(), date=flight_date)
        offer = FlightOffer(
            flight_no="XX000",
            dep_time="08:00",
            arr_time="10:00",
            price=0.0,
            currency="CNY",
            note="placeholder — replace with real parser output in a custom provider",
            raw={"mock": True},
        )
        return SearchResult(
            provider=self.name,
            query=q,
            offers=[offer],
            warnings=["example provider returns mock data only"],
        )
