from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.agents.diagnoser import WeaknessDiagnoser
from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.application.rag.service import RagService
from app.config import (
    CacheBackend,
    LLMBackend,
    MemoryBackend,
    RetrievalBackend,
    Settings,
    get_settings,
)
from app.domain.ports import (
    CachePort,
    ChunkMetadataPort,
    EmbeddingPort,
    LLMPort,
    RetrieverPort,
    StudyMemoryPort,
)
from app.infrastructure.cache.in_memory import InMemoryCache
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.embeddings.caching import CachingEmbedding
from app.infrastructure.embeddings.voyage import VoyageEmbedding
from app.infrastructure.llm.anthropic import AnthropicLLM
from app.infrastructure.llm.caching import CachingLLM
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.llm.resilient import ResilientLLM
from app.infrastructure.orchestration.assistant import AssistantOrchestrator
from app.infrastructure.persistence.chunkmeta_inmemory import InMemoryChunkMetadata
from app.infrastructure.persistence.chunkmeta_sql import SqlChunkMetadata
from app.infrastructure.persistence.engine import create_engine, create_session_factory
from app.infrastructure.persistence.memory_inmemory import InMemoryStudyMemory
from app.infrastructure.persistence.memory_sql import SqlStudyMemory
from app.infrastructure.ratelimit.in_memory import FixedWindowRateLimiter
from app.infrastructure.ratelimit.quota import DailyRequestQuota
from app.infrastructure.resilience.budget import DailyTokenBudget
from app.infrastructure.resilience.circuit_breaker import CircuitBreaker
from app.infrastructure.retrieval.hybrid import HybridRetriever
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.infrastructure.retrieval.qdrant import QdrantRetriever


def _build_embedding(settings: Settings) -> EmbeddingPort:
    embedding: EmbeddingPort = VoyageEmbedding(
        api_key=settings.voyage_api_key, model=settings.embedding_model
    )
    if settings.embedding_cache_enabled:
        return CachingEmbedding(
            embedding,
            get_cache(),
            model=settings.embedding_model,
            ttl_seconds=settings.embedding_cache_ttl_seconds,
        )
    return embedding


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
def get_rate_limiter() -> FixedWindowRateLimiter:
    settings = get_settings()
    return FixedWindowRateLimiter(
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


@lru_cache(maxsize=1)
def get_request_quota() -> DailyRequestQuota:
    settings = get_settings()
    return DailyRequestQuota(limit=settings.daily_request_quota)


@lru_cache(maxsize=1)
def get_cache() -> CachePort:
    settings = get_settings()
    if settings.cache_backend is CacheBackend.REDIS:
        return RedisCache(url=settings.redis_url)
    return InMemoryCache()


@lru_cache(maxsize=1)
def get_llm() -> LLMPort:
    settings = get_settings()
    if settings.llm_backend is not LLMBackend.ANTHROPIC:
        return EchoLLM()
    breaker = CircuitBreaker(
        failure_threshold=settings.breaker_failure_threshold,
        reset_timeout=settings.breaker_reset_timeout,
    )
    resilient = ResilientLLM(
        inner=AnthropicLLM(api_key=settings.anthropic_api_key),
        breaker=breaker,
        attempts=settings.llm_max_retries,
        base_delay=settings.llm_retry_base_delay,
        timeout=settings.llm_timeout_seconds,
        budget=DailyTokenBudget(settings.daily_token_budget),
    )
    if settings.llm_cache_enabled:
        return CachingLLM(resilient, get_cache(), ttl_seconds=settings.llm_cache_ttl_seconds)
    return resilient


def get_rag_service() -> RagService:
    settings = get_settings()
    return RagService(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_standard,
        max_tokens=settings.max_tokens_per_request,
        top_k=settings.top_k,
    )


def get_quiz_generator() -> QuizGenerator:
    settings = get_settings()
    return QuizGenerator(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_standard,
        max_tokens=settings.max_tokens_per_request,
        top_k=settings.top_k,
    )


def get_study_planner() -> StudyPlanner:
    settings = get_settings()
    return StudyPlanner(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_standard,
        max_tokens=settings.max_tokens_per_request,
        top_k=settings.top_k,
    )


def get_weakness_diagnoser() -> WeaknessDiagnoser:
    settings = get_settings()
    return WeaknessDiagnoser(
        retriever=get_retriever(),
        llm=get_llm(),
        model=settings.llm_model_deep,
        max_tokens=settings.max_tokens_per_request,
        top_k=settings.top_k,
    )


@lru_cache(maxsize=1)
def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    return create_session_factory(create_engine(settings.database_url))


@lru_cache(maxsize=1)
def get_study_memory() -> StudyMemoryPort:
    settings = get_settings()
    if settings.memory_backend is MemoryBackend.SQL:
        return SqlStudyMemory(_get_session_factory())
    return InMemoryStudyMemory()


@lru_cache(maxsize=1)
def get_chunk_store() -> ChunkMetadataPort:
    settings = get_settings()
    if settings.memory_backend is MemoryBackend.SQL:
        return SqlChunkMetadata(_get_session_factory())
    return InMemoryChunkMetadata()


@lru_cache(maxsize=1)
def get_assistant_orchestrator() -> AssistantOrchestrator:
    return AssistantOrchestrator(
        rag=get_rag_service(),
        quiz=get_quiz_generator(),
        planner=get_study_planner(),
    )
