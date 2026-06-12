from __future__ import annotations

from httpx import AsyncClient


async def test_healthz_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == "local"
    assert isinstance(payload["checks"], dict)


async def test_ingest_then_ask_flow(client: AsyncClient) -> None:
    ingest = await client.post(
        "/ingest",
        json={
            "course_id": "c1",
            "source": "bio.pdf",
            "text": "La photosynthèse transforme la lumière en énergie chimique.",
        },
    )
    assert ingest.status_code == 201
    assert ingest.json()["chunks_created"] >= 1

    ask = await client.post(
        "/ask", json={"course_id": "c1", "question": "Rôle de la photosynthèse ?"}
    )
    assert ask.status_code == 200
    body = ask.json()
    assert body["grounded"] is True
    assert body["citations"]


async def test_ingest_file_then_ask_flow(client: AsyncClient) -> None:
    files = {
        "file": (
            "bio.txt",
            "La photosynthèse transforme la lumière en énergie.".encode(),
            "text/plain",
        )
    }
    ingest = await client.post("/ingest/file", files=files, data={"course_id": "c2"})
    assert ingest.status_code == 201
    assert ingest.json()["chunks_created"] >= 1

    ask = await client.post(
        "/ask", json={"course_id": "c2", "question": "Que fait la photosynthèse ?"}
    )
    assert ask.status_code == 200
    assert ask.json()["grounded"] is True


async def test_ingest_file_rejects_unsupported_type(client: AsyncClient) -> None:
    files = {"file": ("image.png", b"\x89PNG", "image/png")}
    response = await client.post("/ingest/file", files=files, data={"course_id": "c2"})
    assert response.status_code == 415


async def test_ask_without_corpus_returns_422(client: AsyncClient) -> None:
    response = await client.post("/ask", json={"course_id": "vide", "question": "Une question ?"})
    assert response.status_code == 422
