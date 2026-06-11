from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    def __init__(self) -> None:
        super().__init__("Circuit breaker ouvert: appel rejeté.")


class CircuitBreaker:
    """Circuit breaker minimal et testable (horloge injectable)."""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._clock = clock
        self._failures = 0
        self._opened_at: float | None = None
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        return self._state

    def _can_attempt(self) -> bool:
        if self._state is not CircuitState.OPEN:
            return True
        if self._opened_at is None:
            return True
        if self._clock() - self._opened_at >= self._reset_timeout:
            self._state = CircuitState.HALF_OPEN
            return True
        return False

    def _on_success(self) -> None:
        self._failures = 0
        self._opened_at = None
        self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        self._failures += 1
        if self._state is CircuitState.HALF_OPEN or self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = self._clock()

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        if not self._can_attempt():
            raise CircuitBreakerOpenError
        try:
            result = await func()
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result
