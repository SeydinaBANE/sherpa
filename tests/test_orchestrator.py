from __future__ import annotations

from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.application.ingestion.chunker import chunk_document
from app.application.rag.service import RagService
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.orchestration.assistant import AssistantOrchestrator
from app.infrastructure.retrieval.in_memory import InMemoryRetriever

QUIZ_JSON = (
    '{"questions":[{"question":"Que capte la photosynthèse ?",'
    '"choices":["la lumière","le son"],"answer_index":0,"explanation":"voir le cours"}]}'
)
PLAN_JSON = '{"items":[{"day":1,"topic":"Photosynthèse","activities":["lire"]}]}'


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        return self._reply


async def _orchestrator() -> AssistantOrchestrator:
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    return AssistantOrchestrator(
        rag=RagService(retriever, EchoLLM(), "m", 512),
        quiz=QuizGenerator(retriever, _FakeLLM(QUIZ_JSON), "m", 512),
        planner=StudyPlanner(retriever, _FakeLLM(PLAN_JSON), "m", 512),
    )


async def test_orchestrator_routes_to_quiz() -> None:
    orchestrator = await _orchestrator()
    state = await orchestrator.run("c1", "Donne-moi un quiz sur la photosynthèse")
    assert state["intent"] == "quiz"
    assert state["quiz"] is not None
    assert state["answer"] is None


async def test_orchestrator_routes_to_plan() -> None:
    orchestrator = await _orchestrator()
    state = await orchestrator.run("c1", "Fais un plan de révision photosynthèse")
    assert state["intent"] == "plan"
    assert state["plan"] is not None


async def test_orchestrator_routes_to_tutor() -> None:
    orchestrator = await _orchestrator()
    state = await orchestrator.run("c1", "Explique la photosynthèse")
    assert state["intent"] == "tutor"
    assert state["answer"] is not None
    assert state["answer"].is_grounded
