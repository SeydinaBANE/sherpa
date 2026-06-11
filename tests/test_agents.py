from __future__ import annotations

import pytest
from app.application.agents.base import parse_model
from app.application.agents.diagnoser import WeaknessDiagnoser
from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.application.ingestion.chunker import chunk_document
from app.domain.agents import AnswerRecord
from app.domain.exceptions import AgentOutputError, NoRelevantContextError
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from pydantic import BaseModel

QUIZ_JSON = (
    '{"questions":[{"question":"Que capte la photosynthèse ?",'
    '"choices":["la lumière","le son"],"answer_index":0,"explanation":"voir le cours"}]}'
)
PLAN_JSON = '{"items":[{"day":1,"topic":"Photosynthèse","activities":["lire","quiz"]}]}'
DIAG_JSON = '{"weak_topics":["photosynthèse"],"recommendation":"revoir le chapitre"}'


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.last_prompt = ""

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        self.last_prompt = prompt
        return self._reply


async def _retriever_with_corpus() -> InMemoryRetriever:
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    return retriever


async def test_quiz_generator_parses_and_grounds() -> None:
    retriever = await _retriever_with_corpus()
    fake = _FakeLLM(QUIZ_JSON)
    quiz = await QuizGenerator(retriever, fake, "m", 512).generate("c1", "photosynthèse", 1)
    assert len(quiz.questions) == 1
    assert quiz.questions[0].answer_index == 0
    assert "CONTEXTE" in fake.last_prompt


async def test_quiz_generator_invalid_json_raises() -> None:
    retriever = await _retriever_with_corpus()
    with pytest.raises(AgentOutputError):
        await QuizGenerator(retriever, _FakeLLM("pas du json"), "m", 512).generate(
            "c1", "photosynthèse", 1
        )


async def test_quiz_generator_without_context_raises() -> None:
    with pytest.raises(NoRelevantContextError):
        await QuizGenerator(InMemoryRetriever(), _FakeLLM(QUIZ_JSON), "m", 512).generate(
            "vide", "sujet", 1
        )


async def test_study_planner_parses() -> None:
    retriever = await _retriever_with_corpus()
    plan = await StudyPlanner(retriever, _FakeLLM(PLAN_JSON), "m", 512).generate(
        "c1", "photosynthèse", 3
    )
    assert plan.items[0].day == 1
    assert "lire" in plan.items[0].activities


async def test_diagnoser_parses() -> None:
    retriever = await _retriever_with_corpus()
    answers = [AnswerRecord(question="Que fait la photosynthèse ?", correct=False)]
    report = await WeaknessDiagnoser(retriever, _FakeLLM(DIAG_JSON), "m", 512).diagnose(
        "c1", answers
    )
    assert "photosynthèse" in report.weak_topics
    assert report.recommendation


def test_parse_model_handles_fenced_json() -> None:
    class _Model(BaseModel):
        x: int

    assert parse_model('```json\n{"x": 5}\n```', _Model).x == 5
