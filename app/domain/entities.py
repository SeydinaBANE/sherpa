from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class Chunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str
    course_id: str
    source: str
    ordinal: int
    text: str

    @classmethod
    def create(cls, course_id: str, source: str, ordinal: int, text: str) -> Chunk:
        digest = hashlib.sha256(f"{course_id}:{source}:{ordinal}:{text}".encode()).hexdigest()
        return cls(
            chunk_id=digest[:32],
            course_id=course_id,
            source=source,
            ordinal=ordinal,
            text=text,
        )


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk: Chunk
    score: float


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    ordinal: int
    snippet: str


class Answer(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    course_id: str
    text: str
    citations: tuple[Citation, ...]
    model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_grounded(self) -> bool:
        return len(self.citations) > 0
