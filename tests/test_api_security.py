from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from app.config import get_settings
from app.presentation import dependencies
from app.presentation.api import create_app
from httpx import ASGITransport, AsyncClient


async def _client() -> AsyncIterator[AsyncClient]:
    get_settings.cache_clear()
    dependencies.get_rate_limiter.cache_clear()
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def _auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHERPA_AUTH_ENABLED", "true")
    monkeypatch.setenv("SHERPA_API_KEYS", "secret-key, other-key")


@pytest.fixture
def _rate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHERPA_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("SHERPA_RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("SHERPA_RATE_LIMIT_WINDOW_SECONDS", "60")


async def test_protected_route_requires_key_when_auth_enabled(_auth_env: None) -> None:
    async for client in _client():
        missing = await client.post("/ask", json={"course_id": "c1", "question": "q ?"})
        assert missing.status_code == 401

        wrong = await client.post(
            "/ask", json={"course_id": "c1", "question": "q ?"}, headers={"X-API-Key": "nope"}
        )
        assert wrong.status_code == 401


async def test_public_routes_stay_open_when_auth_enabled(_auth_env: None) -> None:
    async for client in _client():
        assert (await client.get("/healthz")).status_code == 200
        assert (await client.get("/")).status_code == 200


async def test_valid_key_passes_auth(_auth_env: None) -> None:
    async for client in _client():
        await client.post(
            "/ingest",
            json={"course_id": "c1", "source": "s", "text": "La photosynthèse capte la lumière."},
            headers={"X-API-Key": "secret-key"},
        )
        ok = await client.post(
            "/ask",
            json={"course_id": "c1", "question": "photosynthèse ?"},
            headers={"X-API-Key": "secret-key"},
        )
        assert ok.status_code == 200


async def test_rate_limit_blocks_after_threshold(_rate_env: None) -> None:
    async for client in _client():
        assert (await client.get("/healthz")).status_code == 200  # public, non limité
        first = await client.post("/ask", json={"course_id": "x", "question": "q ?"})
        second = await client.post("/ask", json={"course_id": "x", "question": "q ?"})
        third = await client.post("/ask", json={"course_id": "x", "question": "q ?"})
        assert first.status_code in (200, 422)
        assert second.status_code in (200, 422)
        assert third.status_code == 429
