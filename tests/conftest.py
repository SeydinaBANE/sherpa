from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
from app.config import get_settings
from app.presentation import dependencies
from app.presentation.api import create_app
from httpx import ASGITransport, AsyncClient


def _clear_caches() -> None:
    get_settings.cache_clear()
    dependencies.get_retriever.cache_clear()
    dependencies.get_llm.cache_clear()
    dependencies.get_study_memory.cache_clear()
    dependencies.get_chunk_store.cache_clear()
    dependencies._get_session_factory.cache_clear()
    dependencies.get_cache.cache_clear()
    dependencies.get_rate_limiter.cache_clear()


@pytest.fixture(autouse=True)
def _reset_singletons() -> Iterator[None]:
    _clear_caches()
    yield
    _clear_caches()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
