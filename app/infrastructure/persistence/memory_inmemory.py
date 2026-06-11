from __future__ import annotations

from app.domain.memory import StudyEvent


class InMemoryStudyMemory:
    """Adapter mémoire par défaut (hors-ligne) implémentant StudyMemoryPort."""

    def __init__(self) -> None:
        self._events: list[StudyEvent] = []

    async def record(self, events: list[StudyEvent]) -> int:
        self._events.extend(events)
        return len(events)

    async def history(self, student_id: str, course_id: str) -> list[StudyEvent]:
        return [
            event
            for event in self._events
            if event.student_id == student_id and event.course_id == course_id
        ]
