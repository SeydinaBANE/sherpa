from __future__ import annotations

import hashlib

from app.domain.ports import CachePort, LLMPort


def _cache_key(system: str, prompt: str, model: str, max_tokens: int) -> str:
    raw = "\x00".join([model, str(max_tokens), system, prompt])
    return "llm:" + hashlib.sha256(raw.encode()).hexdigest()


class CachingLLM:
    """Décore un LLMPort d'un cache (court-circuite les complétions identiques)."""

    def __init__(self, inner: LLMPort, cache: CachePort, ttl_seconds: int = 3600) -> None:
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        key = _cache_key(system, prompt, model, max_tokens)
        cached = await self._cache.get(key)
        if cached is not None:
            return cached
        result = await self._inner.complete(
            system=system, prompt=prompt, model=model, max_tokens=max_tokens
        )
        await self._cache.set(key, result, self._ttl)
        return result
