from __future__ import annotations

import pytest
from app.application.ingestion.chunker import chunk_document
from app.infrastructure.retrieval.in_memory import InMemoryRetriever


@pytest.fixture
def retriever() -> InMemoryRetriever:
    return InMemoryRetriever()


async def test_index_is_idempotent(retriever: InMemoryRetriever) -> None:
    chunks = chunk_document("c1", "cours.pdf", "La photosynthèse convertit la lumière.")
    first = await retriever.index(chunks)
    second = await retriever.index(chunks)
    assert first == len(chunks)
    assert second == 0


async def test_retrieve_ranks_relevant_chunk_first(retriever: InMemoryRetriever) -> None:
    await retriever.index(chunk_document("c1", "bio.pdf", "La photosynthèse capte la lumière."))
    await retriever.index(chunk_document("c1", "histoire.pdf", "La révolution française de 1789."))
    results = await retriever.retrieve("c1", "photosynthèse lumière", top_k=2)
    assert results
    assert "photosynthèse" in results[0].chunk.text.lower()


async def test_retrieve_unknown_course_returns_empty(retriever: InMemoryRetriever) -> None:
    results = await retriever.retrieve("inconnu", "question", top_k=4)
    assert results == []
