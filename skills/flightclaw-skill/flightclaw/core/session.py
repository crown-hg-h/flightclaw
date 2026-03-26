from __future__ import annotations

from typing import Any

from flightclaw.core.models import SearchQuery, SearchResult


class Session:
    """Minimal session: last query/result for future refine/undo-style flows."""

    def __init__(self) -> None:
        self._last_query: SearchQuery | None = None
        self._last_result: dict[str, Any] | None = None

    def set_last_search(self, query: SearchQuery, result: SearchResult) -> None:
        self._last_query = query
        self._last_result = result.to_json_dict()

    @property
    def last_query(self) -> SearchQuery | None:
        return self._last_query

    @property
    def last_result(self) -> dict[str, Any] | None:
        return self._last_result


_session: Session | None = None


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session
