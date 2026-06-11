from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.content import ChunkRef


class ChunkRefResponse(BaseModel):
    chunk_id: str
    source: str
    ordinal: int
    created_at: datetime

    @classmethod
    def from_domain(cls, ref: ChunkRef) -> ChunkRefResponse:
        return cls(
            chunk_id=ref.chunk_id,
            source=ref.source,
            ordinal=ref.ordinal,
            created_at=ref.created_at,
        )


class CourseChunksResponse(BaseModel):
    course_id: str
    chunks: list[ChunkRefResponse]


class DeleteCourseResponse(BaseModel):
    course_id: str
    vectors_deleted: int
    chunks_deleted: int
