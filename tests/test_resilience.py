from __future__ import annotations

import pytest
from app.domain.exceptions import BudgetExceededError
from app.infrastructure.llm.resilient import ResilientLLM
from app.infrastructure.resilience.budget import DailyTokenBudget
from app.infrastructure.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from app.infrastructure.resilience.retry import retry_async


async def _noop_sleep(_: float) -> None:
    return None


# ─── retry ─────────────────────────────────────────────────────


async def test_retry_succeeds_after_transient_failures() -> None:
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("boom")
        return "ok"

    result = await retry_async(
        flaky, attempts=3, base_delay=0.0, retry_on=(ConnectionError,), sleep=_noop_sleep
    )
    assert result == "ok"
    assert calls["n"] == 3


async def test_retry_raises_after_exhausting_attempts() -> None:
    async def always_fail() -> str:
        raise ConnectionError("boom")

    with pytest.raises(ConnectionError):
        await retry_async(
            always_fail, attempts=2, base_delay=0.0, retry_on=(ConnectionError,), sleep=_noop_sleep
        )


# ─── circuit breaker ───────────────────────────────────────────


async def test_breaker_opens_after_threshold_and_recovers() -> None:
    now = {"t": 0.0}
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=5.0, clock=lambda: now["t"])

    async def fail() -> str:
        raise ConnectionError("boom")

    for _ in range(2):
        with pytest.raises(ConnectionError):
            await breaker.call(fail)
    assert breaker.state is CircuitState.OPEN

    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call(fail)

    now["t"] = 10.0

    async def ok() -> str:
        return "ok"

    assert await breaker.call(ok) == "ok"
    assert breaker.state is CircuitState.CLOSED


# ─── budget ────────────────────────────────────────────────────


async def test_budget_raises_when_exceeded_and_resets_per_day() -> None:
    from datetime import date

    days = {"d": date(2026, 1, 1)}
    budget = DailyTokenBudget(daily_budget=100, today=lambda: days["d"])
    budget.charge(80)
    with pytest.raises(BudgetExceededError):
        budget.charge(30)
    days["d"] = date(2026, 1, 2)
    budget.charge(90)


# ─── ResilientLLM ──────────────────────────────────────────────


class _FlakyLLM:
    def __init__(self, failures: int) -> None:
        self._failures = failures
        self.calls = 0

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        self.calls += 1
        if self.calls <= self._failures:
            raise ConnectionError("transient")
        return "réponse"


async def test_resilient_llm_retries_then_succeeds() -> None:
    inner = _FlakyLLM(failures=1)
    llm = ResilientLLM(
        inner=inner, breaker=CircuitBreaker(), attempts=3, base_delay=0.0, sleep=_noop_sleep
    )
    assert await llm.complete(system="s", prompt="p", model="m", max_tokens=10) == "réponse"
    assert inner.calls == 2


async def test_resilient_llm_enforces_budget() -> None:
    llm = ResilientLLM(
        inner=_FlakyLLM(failures=0),
        breaker=CircuitBreaker(),
        budget=DailyTokenBudget(daily_budget=5),
        sleep=_noop_sleep,
    )
    with pytest.raises(BudgetExceededError):
        await llm.complete(system="s", prompt="p", model="m", max_tokens=10)
