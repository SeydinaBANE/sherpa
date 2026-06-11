from __future__ import annotations

from datetime import UTC, datetime

from app.domain.content import ChunkRef
from app.domain.entities import Chunk


class InMemoryChunkMetadata:
    """Adapter métadonnées de chunks par défaut (hors-ligne). Implémente ChunkMetadataPort."""

    def __init__(self) -> None:
        self._refs: dict[str, tuple[str, ChunkRef]] = {}

    async def record(self, chunks: list[Chunk]) -> int:
        added = 0
        for chunk in chunks:
            if chunk.chunk_id in self._refs:
                continue
            ref = ChunkRef(
                chunk_id=chunk.chunk_id,
                source=chunk.source,
                ordinal=chunk.ordinal,
                created_at=datetime.now(UTC),
            )
            self._refs[chunk.chunk_id] = (chunk.course_id, ref)
            added += 1
        return added

    async def list_by_course(self, course_id: str) -> list[ChunkRef]:
        refs = [ref for course, ref in self._refs.values() if course == course_id]
        return sorted(refs, key=lambda ref: ref.ordinal)

    async def delete_course(self, course_id: str) -> int:
        to_remove = [cid for cid, (course, _) in self._refs.items() if course == course_id]
        for chunk_id in to_remove:
            del self._refs[chunk_id]
        return len(to_remove)
