from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol, cast

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.content import ChunkRef
from app.domain.entities import Chunk

from .models import ChunkMetaRow


class _HasRowcount(Protocol):
    rowcount: int


class SqlChunkMetadata:
    """Adapter SQLAlchemy (async) implémentant ChunkMetadataPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def record(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        async with self._session_factory() as session:
            existing = await session.execute(
                select(ChunkMetaRow.chunk_id).where(
                    ChunkMetaRow.chunk_id.in_([chunk.chunk_id for chunk in chunks])
                )
            )
            known = set(existing.scalars().all())
            now = datetime.now(UTC)
            new_rows = [
                ChunkMetaRow(
                    chunk_id=chunk.chunk_id,
                    course_id=chunk.course_id,
                    source=chunk.source,
                    ordinal=chunk.ordinal,
                    created_at=now,
                )
                for chunk in chunks
                if chunk.chunk_id not in known
            ]
            session.add_all(new_rows)
            await session.commit()
        return len(new_rows)

    async def list_by_course(self, course_id: str) -> list[ChunkRef]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ChunkMetaRow)
                .where(ChunkMetaRow.course_id == course_id)
                .order_by(ChunkMetaRow.ordinal)
            )
            rows = result.scalars().all()
        return [
            ChunkRef(
                chunk_id=row.chunk_id,
                source=row.source,
                ordinal=row.ordinal,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def delete_course(self, course_id: str) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                delete(ChunkMetaRow).where(ChunkMetaRow.course_id == course_id)
            )
            await session.commit()
        return cast(_HasRowcount, result).rowcount or 0
