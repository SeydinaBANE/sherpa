from __future__ import annotations

from collections.abc import AsyncIterator

from app.application.agents.diagnoser import WeaknessDiagnoser
from app.application.ingestion.chunker import chunk_document
from app.infrastructure.persistence.memory_inmemory import InMemoryStudyMemory
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.presentation.api import create_app
from app.presentation.dependencies import get_study_memory, get_weakness_diagnoser
from httpx import ASGITransport, AsyncClient

DIAG_JSON = '{"weak_topics":["photosynthèse"],"recommendation":"revoir le chapitre"}'


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        return self._reply


async def test_record_then_history(client: AsyncClient) -> None:
    record = await client.post(
        "/memory/answers",
        json={
            "student_id": "s1",
            "course_id": "c1",
            "answers": [{"question": "Q1 ?", "correct": False}],
        },
    )
    assert record.status_code == 201
    assert record.json()["recorded"] == 1

    history = await client.get("/memory/history", params={"student_id": "s1", "course_id": "c1"})
    assert history.status_code == 200
    assert len(history.json()["events"]) == 1

    deleted = await client.delete("/students/s1")
    assert deleted.status_code == 200
    assert deleted.json()["events_deleted"] == 1
    after = await client.get("/memory/history", params={"student_id": "s1", "course_id": "c1"})
    assert after.json()["events"] == []


async def _client_with_history() -> AsyncIterator[AsyncClient]:
    memory = InMemoryStudyMemory()
    retriever = InMemoryRetriever()
    await retriever.index(
        chunk_document("c1", "bio.pdf", "La photosynthèse transforme la lumière en énergie.")
    )
    app = create_app()
    app.dependency_overrides[get_study_memory] = lambda: memory
    app.dependency_overrides[get_weakness_diagnoser] = lambda: WeaknessDiagnoser(
        retriever, _FakeLLM(DIAG_JSON), "m", 512
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/memory/answers",
            json={
                "student_id": "s1",
                "course_id": "c1",
                "answers": [{"question": "Que fait la photosynthèse ?", "correct": False}],
            },
        )
        yield client


async def test_diagnose_from_history_returns_report() -> None:
    async for client in _client_with_history():
        response = await client.post(
            "/agents/diagnose-from-history",
            json={"student_id": "s1", "course_id": "c1"},
        )
        assert response.status_code == 200
        assert "photosynthèse" in response.json()["weak_topics"]


async def test_diagnose_from_history_without_history_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/agents/diagnose-from-history",
        json={"student_id": "ghost", "course_id": "c1"},
    )
    assert response.status_code == 404
