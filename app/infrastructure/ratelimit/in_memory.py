from __future__ import annotations

import time
from collections.abc import Callable


class FixedWindowRateLimiter:
    """Limiteur fenêtre fixe en mémoire (horloge injectable, état par identité)."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._limit = limit
        self._window = window_seconds
        self._clock = clock
        self._state: dict[str, tuple[int, int]] = {}

    def allow(self, identity: str) -> bool:
        window = int(self._clock() // self._window)
        entry = self._state.get(identity)
        if entry is None or entry[0] != window:
            self._state[identity] = (window, 1)
            return True
        _, count = entry
        if count >= self._limit:
            return False
        self._state[identity] = (window, count + 1)
        return True
