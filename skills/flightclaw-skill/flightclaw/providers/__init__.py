from __future__ import annotations

from flightclaw.providers.base import BaseProvider
from flightclaw.providers.ctrip import CtripProvider
from flightclaw.providers.example import ExampleProvider

PROVIDERS: dict[str, type[BaseProvider]] = {
    "example": ExampleProvider,
    "ctrip": CtripProvider,
}


def get_provider(name: str) -> BaseProvider:
    key = name.lower().strip()
    if key not in PROVIDERS:
        known = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown provider {name!r}. Known: {known}")
    return PROVIDERS[key]()
