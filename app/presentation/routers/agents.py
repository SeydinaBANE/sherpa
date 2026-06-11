from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.agents.diagnoser import WeaknessDiagnoser
from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.domain.agents import AnswerRecord
from app.domain.ports import StudyMemoryPort
from app.presentation.dependencies import (
    get_quiz_generator,
    get_study_memory,
    get_study_planner,
    get_weakness_diagnoser,
)
from app.presentation.schemas_agents import (
    DiagnoseRequest,
    QuizRequest,
    QuizResponse,
    StudyPlanRequest,
    StudyPlanResponse,
    WeaknessReportResponse,
)
from app.presentation.schemas_memory import DiagnoseFromHistoryRequest

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    generator: Annotated[QuizGenerator, Depends(get_quiz_generator)],
) -> QuizResponse:
    quiz = await generator.generate(request.course_id, request.topic, request.num_questions)
    return QuizResponse.from_domain(quiz)


@router.post("/study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    planner: Annotated[StudyPlanner, Depends(get_study_planner)],
) -> StudyPlanResponse:
    plan = await planner.generate(request.course_id, request.topic, request.days)
    return StudyPlanResponse.from_domain(plan)


@router.post("/diagnose", response_model=WeaknessReportResponse)
async def diagnose(
    request: DiagnoseRequest,
    diagnoser: Annotated[WeaknessDiagnoser, Depends(get_weakness_diagnoser)],
) -> WeaknessReportResponse:
    answers = [AnswerRecord(question=a.question, correct=a.correct) for a in request.answers]
    report = await diagnoser.diagnose(request.course_id, answers)
    return WeaknessReportResponse.from_domain(report)


@router.post("/diagnose-from-history", response_model=WeaknessReportResponse)
async def diagnose_from_history(
    request: DiagnoseFromHistoryRequest,
    diagnoser: Annotated[WeaknessDiagnoser, Depends(get_weakness_diagnoser)],
    memory: Annotated[StudyMemoryPort, Depends(get_study_memory)],
) -> WeaknessReportResponse:
    events = await memory.history(request.student_id, request.course_id)
    if not events:
        raise HTTPException(
            status_code=404, detail="Aucun historique pour cet étudiant et ce cours"
        )
    answers = [AnswerRecord(question=event.question, correct=event.correct) for event in events]
    report = await diagnoser.diagnose(request.course_id, answers)
    return WeaknessReportResponse.from_domain(report)
