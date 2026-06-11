from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class RetrievalBackend(StrEnum):
    MEMORY = "memory"
    HYBRID = "hybrid"


class LLMBackend(StrEnum):
    ECHO = "echo"
    ANTHROPIC = "anthropic"


class MemoryBackend(StrEnum):
    MEMORY = "memory"
    SQL = "sql"


class CacheBackend(StrEnum):
    MEMORY = "memory"
    REDIS = "redis"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SHERPA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Environment = Environment.LOCAL
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    anthropic_api_key: str = ""
    llm_model_cheap: str = "claude-haiku-4-5"
    llm_model_standard: str = "claude-sonnet-4-6"
    llm_model_deep: str = "claude-opus-4-8"

    voyage_api_key: str = ""
    embedding_model: str = "voyage-3"

    retrieval_backend: RetrievalBackend = RetrievalBackend.MEMORY
    llm_backend: LLMBackend = LLMBackend.ECHO
    memory_backend: MemoryBackend = MemoryBackend.MEMORY
    cache_backend: CacheBackend = CacheBackend.MEMORY

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sherpa_chunks"
    rrf_k: int = Field(default=60, gt=0)
    top_k: int = Field(default=4, gt=0)

    database_url: str = "postgresql+psycopg://sherpa:sherpa@localhost:5432/sherpa"
    redis_url: str = "redis://localhost:6379/0"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    max_tokens_per_request: int = Field(default=4096, gt=0)
    daily_token_budget: int = Field(default=1_000_000, gt=0)

    llm_cache_enabled: bool = True
    llm_cache_ttl_seconds: int = Field(default=3600, gt=0)
    embedding_cache_enabled: bool = True
    embedding_cache_ttl_seconds: int = Field(default=86_400, gt=0)

    llm_max_retries: int = Field(default=3, ge=1)
    llm_retry_base_delay: float = Field(default=0.2, ge=0)
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    breaker_failure_threshold: int = Field(default=5, ge=1)
    breaker_reset_timeout: float = Field(default=30.0, gt=0)

    @property
    def is_production(self) -> bool:
        return self.env is Environment.PRODUCTION


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
