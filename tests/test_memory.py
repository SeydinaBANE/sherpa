from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from app.domain.memory import StudyEvent
from app.infrastructure.persistence.engine import (
    create_all,
    create_engine,
    create_session_factory,
)
from app.infrastructure.persistence.memory_inmemory import InMemoryStudyMemory
from app.infrastructure.persistence.memory_sql import SqlStudyMemory


def _events() -> list[StudyEvent]:
    return [
        StudyEvent(student_id="s1", course_id="c1", question="Q1 ?", correct=False),
        StudyEvent(student_id="s1", course_id="c1", question="Q2 ?", correct=True),
        StudyEvent(student_id="s2", course_id="c1", question="Q3 ?", correct=True),
    ]


async def test_in_memory_record_and_filter_history() -> None:
    memory = InMemoryStudyMemory()
    recorded = await memory.record(_events())
    assert recorded == 3
    history = await memory.history("s1", "c1")
    assert len(history) == 2
    assert all(event.student_id == "s1" for event in history)


@pytest.fixture
async def sql_memory() -> AsyncIterator[SqlStudyMemory]:
    engine = create_engine("sqlite+aiosqlite://")
    await create_all(engine)
    yield SqlStudyMemory(create_session_factory(engine))
    await engine.dispose()


async def test_sql_record_and_history(sql_memory: SqlStudyMemory) -> None:
    await sql_memory.record(_events())
    history = await sql_memory.history("s1", "c1")
    assert [event.question for event in history] == ["Q1 ?", "Q2 ?"]


async def test_sql_record_empty_is_noop(sql_memory: SqlStudyMemory) -> None:
    assert await sql_memory.record([]) == 0
