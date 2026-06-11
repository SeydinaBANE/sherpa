from __future__ import annotations

from app.infrastructure.cache.in_memory import InMemoryCache
from app.infrastructure.embeddings.caching import CachingEmbedding


class _CountingEmbedding:
    def __init__(self) -> None:
        self.batches: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.batches.append(list(texts))
        return [[float(len(text))] for text in texts]


async def test_caching_embedding_caches_per_text() -> None:
    inner = _CountingEmbedding()
    emb = CachingEmbedding(inner, InMemoryCache(), model="m", ttl_seconds=60)

    first = await emb.embed(["a", "bb"])
    assert first == [[1.0], [2.0]]
    second = await emb.embed(["a", "bb"])
    assert second == [[1.0], [2.0]]
    assert inner.batches == [["a", "bb"]]


async def test_caching_embedding_only_computes_misses() -> None:
    inner = _CountingEmbedding()
    emb = CachingEmbedding(inner, InMemoryCache(), model="m", ttl_seconds=60)

    await emb.embed(["a", "bb"])
    result = await emb.embed(["a", "ccc"])
    assert result == [[1.0], [3.0]]
    assert inner.batches[-1] == ["ccc"]


async def test_caching_embedding_preserves_order_and_handles_empty() -> None:
    inner = _CountingEmbedding()
    emb = CachingEmbedding(inner, InMemoryCache(), model="m", ttl_seconds=60)

    await emb.embed(["a", "bb"])
    assert await emb.embed(["bb", "a"]) == [[2.0], [1.0]]
    assert await emb.embed([]) == []
