from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.memory import StudyEvent
from app.presentation.schemas_agents import AnswerRecordRequest


class RecordAnswersRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=128)
    course_id: str = Field(min_length=1, max_length=128)
    answers: list[AnswerRecordRequest] = Field(min_length=1)


class RecordAnswersResponse(BaseModel):
    recorded: int


class StudyEventResponse(BaseModel):
    question: str
    correct: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, event: StudyEvent) -> StudyEventResponse:
        return cls(question=event.question, correct=event.correct, created_at=event.created_at)


class HistoryResponse(BaseModel):
    student_id: str
    course_id: str
    events: list[StudyEventResponse]


class DiagnoseFromHistoryRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=128)
    course_id: str = Field(min_length=1, max_length=128)
