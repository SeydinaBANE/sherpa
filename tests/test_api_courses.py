from __future__ import annotations

from httpx import AsyncClient


async def test_ingest_lists_then_deletes_course(client: AsyncClient) -> None:
    ingest = await client.post(
        "/ingest",
        json={
            "course_id": "c1",
            "source": "bio.pdf",
            "text": "La photosynthèse transforme la lumière en énergie chimique.",
        },
    )
    assert ingest.status_code == 201

    listed = await client.get("/courses/c1/chunks")
    assert listed.status_code == 200
    assert len(listed.json()["chunks"]) >= 1

    deleted = await client.delete("/courses/c1")
    assert deleted.status_code == 200
    body = deleted.json()
    assert body["chunks_deleted"] >= 1
    assert body["vectors_deleted"] >= 1

    after = await client.get("/courses/c1/chunks")
    assert after.json()["chunks"] == []

    ask = await client.post("/ask", json={"course_id": "c1", "question": "photosynthèse ?"})
    assert ask.status_code == 422
