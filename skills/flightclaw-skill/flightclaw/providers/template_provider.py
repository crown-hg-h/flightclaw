from __future__ import annotations

from datetime import date

from flightclaw.core.models import SearchResult
from flightclaw.providers.base import BaseProvider
from flightclaw.utils.http import fetch_text


class TemplateSiteProvider(BaseProvider):
    """
    Copy to e.g. `my_site.py`, implement `search()`, register in `__init__.py`.

    Do not commit credentials. Respect robots.txt and site ToS.
    """

    name = "template"

    def search(self, origin: str, destination: str, flight_date: date) -> SearchResult:
        raise NotImplementedError("Implement search or subclass TemplateSiteProvider")

    def _fetch_homepage_smoke(self, base_url: str) -> str:
        return fetch_text(base_url)
