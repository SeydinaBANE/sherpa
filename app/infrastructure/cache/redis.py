from __future__ import annotations

from typing import Protocol, cast


class _RedisClient(Protocol):
    async def get(self, name: str) -> str | None: ...

    async def set(self, name: str, value: str, *, ex: int) -> object: ...


class RedisCache:
    """Cache Redis (async) implémentant CachePort. Import lazy, client injectable."""

    def __init__(self, url: str, client: _RedisClient | None = None) -> None:
        self._url = url
        self._client = client

    def _get_client(self) -> _RedisClient:
        if self._client is None:
            from redis.asyncio import Redis

            self._client = cast(_RedisClient, Redis.from_url(self._url, decode_responses=True))
        return self._client

    async def get(self, key: str) -> str | None:
        return await self._get_client().get(key)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._get_client().set(key, value, ex=ttl_seconds)
