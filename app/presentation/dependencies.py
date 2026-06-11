from __future__ import annotations

from functools import lru_cache

from app.application.rag.service import RagService
from app.config import LLMBackend, RetrievalBackend, Settings, get_settings
from app.domain.ports import EmbeddingPort, LLMPort, RetrieverPort
from app.infrastructure.embeddings.voyage import VoyageEmbedding
from app.infrastructure.llm.anthropic import AnthropicLLM
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.retrieval.hybrid import HybridRetriever
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.infrastructure.retrieval.qdrant import QdrantRetriever


def _build_embedding(settings: Settings) -> EmbeddingPort:
    return VoyageEmbedding(api_key=settings.voyage_api_key, model=settings.embedding_model)


@lru_cache(maxsize=1)
def get_retriever() -> RetrieverPort:
    settings = get_settings()
    if settings.retrieval_backend is RetrievalBackend.HYBRID:
        dense = QdrantRetriever(
            url=settings.qdrant_url,
            collection=settings.qdrant_collection,
            embeddings=_build_embedding(settings),
        )
        return HybridRetriever(dense=dense, sparse=InMemoryRetriever(), rrf_k=settings.rrf_k)
    return InMemoryRetriever()


@lru_cache(maxsize=1)
def get_llm() -> LLMPort:
    settings = get_settings()
    if settings.llm_backend is LLMBackend.ANTHROPIC:
        return AnthropicLLM(api_key=settings.anthropic_api_key)
    return EchoLLM()


def get_rag_service() -> RagService:
    settings = get_settings()
    return RagService(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_standard,
        max_tokens=settings.max_tokens_per_request,
        top_k=settings.top_k,
    )
