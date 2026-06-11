from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class QuizQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    choices: tuple[str, ...]
    answer_index: int
    explanation: str

    @model_validator(mode="after")
    def _check_answer_index(self) -> QuizQuestion:
        if not self.choices:
            raise ValueError("a quiz question must have at least one choice")
        if not 0 <= self.answer_index < len(self.choices):
            raise ValueError("answer_index out of range")
        return self


class Quiz(BaseModel):
    model_config = ConfigDict(frozen=True)

    course_id: str
    topic: str
    questions: tuple[QuizQuestion, ...]


class StudyPlanItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    day: int
    topic: str
    activities: tuple[str, ...]


class StudyPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    course_id: str
    items: tuple[StudyPlanItem, ...]


class AnswerRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    correct: bool


class WeaknessReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    course_id: str
    weak_topics: tuple[str, ...]
    recommendation: str
