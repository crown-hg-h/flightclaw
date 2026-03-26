from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class FlightOffer(BaseModel):
    flight_no: str = ""
    dep_time: str = ""
    arr_time: str = ""
    price: float = 0.0
    currency: str = "CNY"
    note: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    origin: str
    destination: str
    date: date


class SearchResult(BaseModel):
    provider: str
    query: SearchQuery
    offers: list[FlightOffer] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "query": {
                "origin": self.query.origin,
                "destination": self.query.destination,
                "date": self.query.date.isoformat(),
            },
            "offers": [o.model_dump() for o in self.offers],
            "warnings": self.warnings,
        }
