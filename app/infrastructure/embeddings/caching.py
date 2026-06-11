from __future__ import annotations

import hashlib
import json

from app.domain.ports import CachePort, EmbeddingPort


def _cache_key(model: str, text: str) -> str:
    digest = hashlib.sha256(f"{model}\x00{text}".encode()).hexdigest()
    return f"emb:{digest}"


class CachingEmbedding:
    """Décore un EmbeddingPort d'un cache par texte ; ne calcule que les manquants."""

    def __init__(
        self,
        inner: EmbeddingPort,
        cache: CachePort,
        model: str,
        ttl_seconds: int = 86_400,
    ) -> None:
        self._inner = inner
        self._cache = cache
        self._model = model
        self._ttl = ttl_seconds

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float] | None] = [None] * len(texts)
        missing_indexes: list[int] = []
        missing_texts: list[str] = []
        for index, text in enumerate(texts):
            cached = await self._cache.get(_cache_key(self._model, text))
            if cached is not None:
                results[index] = json.loads(cached)
            else:
                missing_indexes.append(index)
                missing_texts.append(text)
        if missing_texts:
            fresh = await self._inner.embed(missing_texts)
            for index, vector in zip(missing_indexes, fresh, strict=True):
                results[index] = vector
                await self._cache.set(
                    _cache_key(self._model, texts[index]), json.dumps(vector), self._ttl
                )
        return [vector for vector in results if vector is not None]
