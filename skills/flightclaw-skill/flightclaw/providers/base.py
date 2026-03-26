from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from flightclaw.core.models import SearchResult


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search(self, origin: str, destination: str, flight_date: date) -> SearchResult:
        """Return structured offers for the given O&D and local date."""
