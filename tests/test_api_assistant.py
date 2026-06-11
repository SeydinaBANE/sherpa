from __future__ import annotations

from collections.abc import AsyncIterator

from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.application.ingestion.chunker import chunk_document
from app.application.rag.service import RagService
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.orchestration.assistant import AssistantOrchestrator
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.presentation.api import create_app
from app.presentation.dependencies import get_assistant_orchestrator
from httpx import ASGITransport, AsyncClient

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


async def _client() -> AsyncIterator[AsyncClient]:
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    orchestrator = AssistantOrchestrator(
        rag=RagService(retriever, EchoLLM(), "m", 512),
        quiz=QuizGenerator(retriever, _FakeLLM(QUIZ_JSON), "m", 512),
        planner=StudyPlanner(retriever, _FakeLLM(PLAN_JSON), "m", 512),
    )
    app = create_app()
    app.dependency_overrides[get_assistant_orchestrator] = lambda: orchestrator
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_assistant_endpoint_routes_quiz() -> None:
    async for client in _client():
        response = await client.post(
            "/assistant",
            json={"course_id": "c1", "message": "Donne-moi un quiz sur la photosynthèse"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "quiz"
        assert body["quiz"] is not None
        assert body["answer"] is None


async def test_assistant_endpoint_routes_tutor() -> None:
    async for client in _client():
        response = await client.post(
            "/assistant",
            json={"course_id": "c1", "message": "Explique la photosynthèse"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "tutor"
        assert body["answer"]["grounded"] is True
