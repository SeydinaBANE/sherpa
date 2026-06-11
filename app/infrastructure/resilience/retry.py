from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

Sleeper = Callable[[float], Awaitable[None]]


async def retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    base_delay: float,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    sleep: Sleeper = asyncio.sleep,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    for attempt in range(attempts):
        try:
            return await func()
        except Exception as error:
            if not isinstance(error, retry_on) or attempt == attempts - 1:
                raise
            await sleep(base_delay * (2**attempt))
    raise RuntimeError("unreachable")  # pragma: no cover
