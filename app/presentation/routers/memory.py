from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.domain.memory import StudyEvent
from app.domain.ports import StudyMemoryPort
from app.presentation.dependencies import get_study_memory
from app.presentation.schemas_memory import (
    HistoryResponse,
    RecordAnswersRequest,
    RecordAnswersResponse,
    StudyEventResponse,
)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/answers", response_model=RecordAnswersResponse, status_code=201)
async def record_answers(
    request: RecordAnswersRequest,
    memory: Annotated[StudyMemoryPort, Depends(get_study_memory)],
) -> RecordAnswersResponse:
    events = [
        StudyEvent(
            student_id=request.student_id,
            course_id=request.course_id,
            question=answer.question,
            correct=answer.correct,
        )
        for answer in request.answers
    ]
    recorded = await memory.record(events)
    return RecordAnswersResponse(recorded=recorded)


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    memory: Annotated[StudyMemoryPort, Depends(get_study_memory)],
    student_id: Annotated[str, Query(min_length=1, max_length=128)],
    course_id: Annotated[str, Query(min_length=1, max_length=128)],
) -> HistoryResponse:
    events = await memory.history(student_id, course_id)
    return HistoryResponse(
        student_id=student_id,
        course_id=course_id,
        events=[StudyEventResponse.from_domain(event) for event in events],
    )
