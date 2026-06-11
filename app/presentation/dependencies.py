from __future__ import annotations

from functools import lru_cache

from app.application.rag.service import RagService
from app.config import Settings, get_settings
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.retrieval.in_memory import InMemoryRetriever


@lru_cache(maxsize=1)
def get_retriever() -> InMemoryRetriever:
    return InMemoryRetriever()


@lru_cache(maxsize=1)
def get_llm() -> EchoLLM:
    return EchoLLM()


def get_rag_service() -> RagService:
    settings: Settings = get_settings()
    return RagService(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_standard,
        max_tokens=settings.max_tokens_per_request,
    )
