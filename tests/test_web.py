from __future__ import annotations

from httpx import AsyncClient


async def test_index_serves_html(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Sherpa" in response.text
