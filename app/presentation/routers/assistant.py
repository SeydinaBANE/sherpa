from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.infrastructure.orchestration.assistant import AssistantOrchestrator
from app.presentation.dependencies import get_assistant_orchestrator
from app.presentation.schemas import AskResponse
from app.presentation.schemas_agents import (
    AssistantRequest,
    AssistantResponse,
    QuizResponse,
    StudyPlanResponse,
)

router = APIRouter(tags=["assistant"])


@router.post("/assistant", response_model=AssistantResponse)
async def assistant(
    request: AssistantRequest,
    orchestrator: Annotated[AssistantOrchestrator, Depends(get_assistant_orchestrator)],
) -> AssistantResponse:
    state = await orchestrator.run(request.course_id, request.message)
    answer = state["answer"]
    quiz = state["quiz"]
    plan = state["plan"]
    return AssistantResponse(
        intent=state["intent"],
        answer=AskResponse.from_domain(answer) if answer is not None else None,
        quiz=QuizResponse.from_domain(quiz) if quiz is not None else None,
        plan=StudyPlanResponse.from_domain(plan) if plan is not None else None,
    )
