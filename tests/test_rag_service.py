from __future__ import annotations

import pytest
from app.application.ingestion.chunker import chunk_document
from app.application.rag.service import RagService
from app.domain.exceptions import NoRelevantContextError
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.retrieval.in_memory import InMemoryRetriever


async def _service_with_corpus() -> RagService:
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    return RagService(retriever=retriever, llm=EchoLLM(), model="claude-sonnet-4-6", max_tokens=512)


async def test_answer_is_grounded_with_citations() -> None:
    service = await _service_with_corpus()
    answer = await service.answer("c1", "Que fait la photosynthèse ?")
    assert answer.is_grounded
    assert answer.citations
    assert answer.model == "claude-sonnet-4-6"


async def test_answer_without_context_raises() -> None:
    service = RagService(retriever=InMemoryRetriever(), llm=EchoLLM(), model="m", max_tokens=512)
    with pytest.raises(NoRelevantContextError):
        await service.answer("vide", "question sans corpus")
