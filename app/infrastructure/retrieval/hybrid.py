from __future__ import annotations

from app.domain.entities import Chunk, RetrievedChunk
from app.domain.ports import RetrieverPort

from .fusion import DEFAULT_RRF_K, reciprocal_rank_fusion


class HybridRetriever:
    """Combine un retriever dense et un retriever sparse via fusion RRF (RetrieverPort)."""

    def __init__(
        self,
        dense: RetrieverPort,
        sparse: RetrieverPort,
        rrf_k: int = DEFAULT_RRF_K,
    ) -> None:
        self._dense = dense
        self._sparse = sparse
        self._rrf_k = rrf_k

    async def index(self, chunks: list[Chunk]) -> int:
        dense_added = await self._dense.index(chunks)
        await self._sparse.index(chunks)
        return dense_added

    async def delete_course(self, course_id: str) -> int:
        deleted = await self._dense.delete_course(course_id)
        await self._sparse.delete_course(course_id)
        return deleted

    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]:
        dense = await self._dense.retrieve(course_id, query, top_k)
        sparse = await self._sparse.retrieve(course_id, query, top_k)
        return reciprocal_rank_fusion([dense, sparse], self._rrf_k)[:top_k]
