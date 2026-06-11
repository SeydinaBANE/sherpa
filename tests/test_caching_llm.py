from __future__ import annotations

from app.infrastructure.cache.in_memory import InMemoryCache
from app.infrastructure.llm.caching import CachingLLM


class _CountingLLM:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        self.calls += 1
        return f"réponse {self.calls}"


async def test_caching_llm_serves_identical_prompt_from_cache() -> None:
    inner = _CountingLLM()
    llm = CachingLLM(inner, InMemoryCache(), ttl_seconds=60)
    first = await llm.complete(system="s", prompt="p", model="m", max_tokens=10)
    second = await llm.complete(system="s", prompt="p", model="m", max_tokens=10)
    assert first == second == "réponse 1"
    assert inner.calls == 1


async def test_caching_llm_distinguishes_prompts() -> None:
    inner = _CountingLLM()
    llm = CachingLLM(inner, InMemoryCache(), ttl_seconds=60)
    await llm.complete(system="s", prompt="p1", model="m", max_tokens=10)
    await llm.complete(system="s", prompt="p2", model="m", max_tokens=10)
    assert inner.calls == 2
