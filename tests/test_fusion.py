from __future__ import annotations

import pytest
from app.domain.entities import Chunk, RetrievedChunk
from app.infrastructure.retrieval.fusion import reciprocal_rank_fusion


def _ranked(course_id: str, texts: list[str]) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(chunk=Chunk.create(course_id, "src", ordinal, text), score=0.0)
        for ordinal, text in enumerate(texts)
    ]


def test_rrf_boosts_items_ranked_high_in_both_lists() -> None:
    shared = Chunk.create("c1", "src", 0, "shared")
    dense = [RetrievedChunk(chunk=shared, score=0.9), *_ranked("c1", ["only-dense"])]
    sparse = [RetrievedChunk(chunk=shared, score=0.5), *_ranked("c1", ["only-sparse"])]
    fused = reciprocal_rank_fusion([dense, sparse])
    assert fused[0].chunk.chunk_id == shared.chunk_id


def test_rrf_deduplicates_by_chunk_id() -> None:
    chunk = Chunk.create("c1", "src", 0, "x")
    item = RetrievedChunk(chunk=chunk, score=0.0)
    fused = reciprocal_rank_fusion([[item], [item]])
    assert len(fused) == 1


def test_rrf_rejects_non_positive_k() -> None:
    with pytest.raises(ValueError, match="k must be positive"):
        reciprocal_rank_fusion([], k=0)
