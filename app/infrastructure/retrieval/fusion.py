from __future__ import annotations

from app.domain.entities import Chunk, RetrievedChunk

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    rankings: list[list[RetrievedChunk]],
    k: int = DEFAULT_RRF_K,
) -> list[RetrievedChunk]:
    if k <= 0:
        raise ValueError("k must be positive")
    scores: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking):
            chunk_id = item.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
            chunks[chunk_id] = item.chunk
    fused = [
        RetrievedChunk(chunk=chunks[chunk_id], score=score) for chunk_id, score in scores.items()
    ]
    fused.sort(key=lambda item: item.score, reverse=True)
    return fused
