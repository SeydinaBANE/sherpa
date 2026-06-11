from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.memory import StudyEvent

from .models import StudyEventRow


class SqlStudyMemory:
    """Adapter SQLAlchemy (async) implémentant StudyMemoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def record(self, events: list[StudyEvent]) -> int:
        if not events:
            return 0
        async with self._session_factory() as session:
            session.add_all(
                StudyEventRow(
                    student_id=event.student_id,
                    course_id=event.course_id,
                    question=event.question,
                    correct=event.correct,
                    created_at=event.created_at,
                )
                for event in events
            )
            await session.commit()
        return len(events)

    async def history(self, student_id: str, course_id: str) -> list[StudyEvent]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(StudyEventRow)
                .where(
                    StudyEventRow.student_id == student_id,
                    StudyEventRow.course_id == course_id,
                )
                .order_by(StudyEventRow.id)
            )
            rows = result.scalars().all()
        return [
            StudyEvent(
                student_id=row.student_id,
                course_id=row.course_id,
                question=row.question,
                correct=row.correct,
                created_at=row.created_at,
            )
            for row in rows
        ]
