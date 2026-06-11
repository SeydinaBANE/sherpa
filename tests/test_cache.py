from __future__ import annotations

from app.infrastructure.cache.in_memory import InMemoryCache


async def test_cache_set_then_get() -> None:
    cache = InMemoryCache()
    await cache.set("k", "v", ttl_seconds=60)
    assert await cache.get("k") == "v"


async def test_cache_miss_returns_none() -> None:
    cache = InMemoryCache()
    assert await cache.get("absent") is None


async def test_cache_entry_expires() -> None:
    now = {"t": 0.0}
    cache = InMemoryCache(clock=lambda: now["t"])
    await cache.set("k", "v", ttl_seconds=10)
    now["t"] = 9.0
    assert await cache.get("k") == "v"
    now["t"] = 10.0
    assert await cache.get("k") is None
