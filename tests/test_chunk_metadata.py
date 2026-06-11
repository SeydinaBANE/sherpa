from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from app.application.ingestion.chunker import chunk_document
from app.infrastructure.persistence.chunkmeta_inmemory import InMemoryChunkMetadata
from app.infrastructure.persistence.chunkmeta_sql import SqlChunkMetadata
from app.infrastructure.persistence.engine import (
    create_all,
    create_engine,
    create_session_factory,
)


def _chunks() -> list:
    return chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière.")


async def test_in_memory_record_list_delete() -> None:
    store = InMemoryChunkMetadata()
    chunks = _chunks()
    assert await store.record(chunks) == len(chunks)
    assert await store.record(chunks) == 0  # idempotent
    refs = await store.list_by_course("c1")
    assert len(refs) == len(chunks)
    assert await store.delete_course("c1") == len(chunks)
    assert await store.list_by_course("c1") == []


@pytest.fixture
async def sql_store() -> AsyncIterator[SqlChunkMetadata]:
    engine = create_engine("sqlite+aiosqlite://")
    await create_all(engine)
    yield SqlChunkMetadata(create_session_factory(engine))
    await engine.dispose()


async def test_sql_record_list_delete(sql_store: SqlChunkMetadata) -> None:
    chunks = _chunks()
    assert await sql_store.record(chunks) == len(chunks)
    assert await sql_store.record(chunks) == 0
    refs = await sql_store.list_by_course("c1")
    assert [ref.ordinal for ref in refs] == list(range(len(chunks)))
    assert await sql_store.delete_course("c1") == len(chunks)
    assert await sql_store.list_by_course("c1") == []
