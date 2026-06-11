from __future__ import annotations

from app.domain.entities import Chunk, RetrievedChunk
from app.infrastructure.retrieval.hybrid import HybridRetriever


class _StubRetriever:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self._results = results
        self.indexed = 0

    async def index(self, chunks: list[Chunk]) -> int:
        self.indexed += len(chunks)
        return len(chunks)

    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]:
        return self._results[:top_k]


def _item(text: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(chunk=Chunk.create("c1", "src", 0, text), score=score)


async def test_hybrid_indexes_both_backends() -> None:
    dense = _StubRetriever([])
    sparse = _StubRetriever([])
    hybrid = HybridRetriever(dense=dense, sparse=sparse)
    added = await hybrid.index([Chunk.create("c1", "src", 0, "a")])
    assert added == 1
    assert dense.indexed == 1
    assert sparse.indexed == 1


async def test_hybrid_fuses_and_truncates_to_top_k() -> None:
    shared = _item("shared", 1.0)
    dense = _StubRetriever([shared, _item("d", 0.4)])
    sparse = _StubRetriever([shared, _item("s", 0.3)])
    hybrid = HybridRetriever(dense=dense, sparse=sparse)
    results = await hybrid.retrieve("c1", "q", top_k=2)
    assert len(results) == 2
    assert results[0].chunk.chunk_id == shared.chunk.chunk_id
