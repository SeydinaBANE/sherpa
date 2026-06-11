from __future__ import annotations

from collections.abc import AsyncIterator

from app.application.agents.quiz import QuizGenerator
from app.application.ingestion.chunker import chunk_document
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.presentation.api import create_app
from app.presentation.dependencies import get_quiz_generator
from httpx import ASGITransport, AsyncClient

QUIZ_JSON = (
    '{"questions":[{"question":"Que capte la photosynthèse ?",'
    '"choices":["la lumière","le son"],"answer_index":0,"explanation":"voir le cours"}]}'
)


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        return self._reply


async def _client_with_quiz_llm(reply: str) -> AsyncIterator[AsyncClient]:
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    app = create_app()
    app.dependency_overrides[get_quiz_generator] = lambda: QuizGenerator(
        retriever, _FakeLLM(reply), "m", 512
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_quiz_endpoint_returns_quiz() -> None:
    async for client in _client_with_quiz_llm(QUIZ_JSON):
        response = await client.post(
            "/agents/quiz",
            json={"course_id": "c1", "topic": "photosynthèse", "num_questions": 1},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["questions"]) == 1
        assert body["questions"][0]["answer_index"] == 0


async def test_quiz_endpoint_invalid_llm_output_returns_502() -> None:
    async for client in _client_with_quiz_llm("pas du json"):
        response = await client.post(
            "/agents/quiz",
            json={"course_id": "c1", "topic": "photosynthèse", "num_questions": 1},
        )
        assert response.status_code == 502
