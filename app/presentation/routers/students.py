from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.domain.ports import StudyMemoryPort
from app.presentation.dependencies import get_study_memory
from app.presentation.schemas_memory import DeleteStudentResponse

router = APIRouter(prefix="/students", tags=["students"])


@router.delete("/{student_id}", response_model=DeleteStudentResponse)
async def delete_student(
    student_id: Annotated[str, Path(min_length=1, max_length=128)],
    memory: Annotated[StudyMemoryPort, Depends(get_study_memory)],
) -> DeleteStudentResponse:
    deleted = await memory.delete_student(student_id)
    return DeleteStudentResponse(student_id=student_id, events_deleted=deleted)
