from __future__ import annotations

from typing import Protocol

from app.domain.entities import Chunk, RetrievedChunk


class EmbeddingPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class RetrieverPort(Protocol):
    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]: ...

    async def index(self, chunks: list[Chunk]) -> int: ...


class LLMPort(Protocol):
    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str: ...
