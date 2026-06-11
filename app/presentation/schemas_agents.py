from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.agents import Quiz, StudyPlan, WeaknessReport
from app.presentation.schemas import AskResponse


class QuizRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    topic: str = Field(min_length=1, max_length=256)
    num_questions: int = Field(default=5, ge=1, le=20)


class QuizQuestionResponse(BaseModel):
    question: str
    choices: list[str]
    answer_index: int
    explanation: str


class QuizResponse(BaseModel):
    course_id: str
    topic: str
    questions: list[QuizQuestionResponse]

    @classmethod
    def from_domain(cls, quiz: Quiz) -> QuizResponse:
        return cls(
            course_id=quiz.course_id,
            topic=quiz.topic,
            questions=[
                QuizQuestionResponse(
                    question=q.question,
                    choices=list(q.choices),
                    answer_index=q.answer_index,
                    explanation=q.explanation,
                )
                for q in quiz.questions
            ],
        )


class StudyPlanRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    topic: str = Field(min_length=1, max_length=256)
    days: int = Field(default=7, ge=1, le=90)


class StudyPlanItemResponse(BaseModel):
    day: int
    topic: str
    activities: list[str]


class StudyPlanResponse(BaseModel):
    course_id: str
    items: list[StudyPlanItemResponse]

    @classmethod
    def from_domain(cls, plan: StudyPlan) -> StudyPlanResponse:
        return cls(
            course_id=plan.course_id,
            items=[
                StudyPlanItemResponse(day=i.day, topic=i.topic, activities=list(i.activities))
                for i in plan.items
            ],
        )


class AnswerRecordRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    correct: bool


class DiagnoseRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    answers: list[AnswerRecordRequest] = Field(min_length=1)


class WeaknessReportResponse(BaseModel):
    course_id: str
    weak_topics: list[str]
    recommendation: str

    @classmethod
    def from_domain(cls, report: WeaknessReport) -> WeaknessReportResponse:
        return cls(
            course_id=report.course_id,
            weak_topics=list(report.weak_topics),
            recommendation=report.recommendation,
        )


class AssistantRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=2000)


class AssistantResponse(BaseModel):
    intent: str
    answer: AskResponse | None = None
    quiz: QuizResponse | None = None
    plan: StudyPlanResponse | None = None
