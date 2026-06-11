from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    student_id: str
    course_id: str
    question: str
    correct: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
