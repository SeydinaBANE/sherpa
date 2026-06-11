from __future__ import annotations

from typing import Protocol

from app.domain.content import ChunkRef
from app.domain.entities import Chunk, RetrievedChunk
from app.domain.memory import StudyEvent


class EmbeddingPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class RetrieverPort(Protocol):
    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]: ...

    async def index(self, chunks: list[Chunk]) -> int: ...

    async def delete_course(self, course_id: str) -> int: ...


class LLMPort(Protocol):
    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str: ...


class StudyMemoryPort(Protocol):
    async def record(self, events: list[StudyEvent]) -> int: ...

    async def history(self, student_id: str, course_id: str) -> list[StudyEvent]: ...

    async def delete_student(self, student_id: str) -> int: ...


class CachePort(Protocol):
    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, ttl_seconds: int) -> None: ...


class ChunkMetadataPort(Protocol):
    async def record(self, chunks: list[Chunk]) -> int: ...

    async def list_by_course(self, course_id: str) -> list[ChunkRef]: ...

    async def delete_course(self, course_id: str) -> int: ...
