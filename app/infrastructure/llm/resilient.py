from __future__ import annotations

import asyncio

from app.domain.ports import LLMPort
from app.infrastructure.resilience.budget import DailyTokenBudget
from app.infrastructure.resilience.circuit_breaker import CircuitBreaker
from app.infrastructure.resilience.retry import Sleeper, retry_async


class ResilientLLM:
    """Décore un LLMPort avec budget, timeout, retries (backoff) et circuit breaker."""

    def __init__(
        self,
        inner: LLMPort,
        breaker: CircuitBreaker,
        attempts: int = 3,
        base_delay: float = 0.2,
        timeout: float = 30.0,
        budget: DailyTokenBudget | None = None,
        sleep: Sleeper = asyncio.sleep,
    ) -> None:
        self._inner = inner
        self._breaker = breaker
        self._attempts = attempts
        self._base_delay = base_delay
        self._timeout = timeout
        self._budget = budget
        self._sleep = sleep

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        if self._budget is not None:
            self._budget.charge(max_tokens)

        async def _call() -> str:
            return await asyncio.wait_for(
                self._inner.complete(
                    system=system, prompt=prompt, model=model, max_tokens=max_tokens
                ),
                timeout=self._timeout,
            )

        async def _retried() -> str:
            return await retry_async(
                _call,
                attempts=self._attempts,
                base_delay=self._base_delay,
                retry_on=(TimeoutError, ConnectionError),
                sleep=self._sleep,
            )

        return await self._breaker.call(_retried)
