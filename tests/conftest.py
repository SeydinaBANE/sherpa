from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
from app.presentation import dependencies
from app.presentation.api import create_app
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _reset_singletons() -> Iterator[None]:
    dependencies.get_retriever.cache_clear()
    dependencies.get_llm.cache_clear()
    dependencies.get_study_memory.cache_clear()
    yield
    dependencies.get_retriever.cache_clear()
    dependencies.get_llm.cache_clear()
    dependencies.get_study_memory.cache_clear()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
