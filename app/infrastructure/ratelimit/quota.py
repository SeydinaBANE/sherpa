from __future__ import annotations

from collections.abc import Callable
from datetime import date


class DailyRequestQuota:
    """Quota de requêtes par identité et par jour calendaire (`today` injectable)."""

    def __init__(self, limit: int, today: Callable[[], date] = date.today) -> None:
        self._limit = limit
        self._today = today
        self._day: date | None = None
        self._counts: dict[str, int] = {}

    def allow(self, identity: str) -> bool:
        current_day = self._today()
        if current_day != self._day:
            self._day = current_day
            self._counts = {}
        count = self._counts.get(identity, 0)
        if count >= self._limit:
            return False
        self._counts[identity] = count + 1
        return True
