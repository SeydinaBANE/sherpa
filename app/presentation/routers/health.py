from __future__ import annotations

import asyncio

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app import __version__
from app.config import CacheBackend, MemoryBackend, RetrievalBackend, get_settings
from app.infrastructure.observability.metrics import render_metrics
from app.presentation.dependencies import _get_session_factory
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


async def _check_db() -> bool:
    from sqlalchemy import text

    factory = _get_session_factory()
    async with factory() as session:
        await session.execute(text("SELECT 1"))
    return True


async def _check_cache(settings: object) -> bool:
    from redis.asyncio import Redis as _AsyncRedis

    r = _AsyncRedis.from_url(settings.redis_url)  # type: ignore[union-attr]
    await r.ping()
    await r.aclose()
    return True


async def _check_vector_store(settings: object) -> bool:
    from qdrant_client import QdrantClient

    _client = QdrantClient(url=settings.qdrant_url)  # type: ignore[union-attr]
    await asyncio.to_thread(_client.get_collections)
    return True


async def _run_checks(settings: object) -> dict[str, str]:
    checks: dict[str, str] = {}
    tasks: list[tuple[str, object]] = []

    if settings.memory_backend is MemoryBackend.SQL:  # type: ignore[union-attr]
        tasks.append(("database", _check_db()))
    if settings.cache_backend is CacheBackend.REDIS:  # type: ignore[union-attr]
        tasks.append(("cache", _check_cache(settings)))
    if settings.retrieval_backend is RetrievalBackend.HYBRID:  # type: ignore[union-attr]
        tasks.append(("vector_store", _check_vector_store(settings)))

    async def _check_one(name: str, coro: object) -> tuple[str, str]:
        try:
            await coro  # type: ignore[arg-type]
            return name, "ok"
        except Exception:
            return name, "unhealthy"

    results = await asyncio.gather(*(_check_one(n, c) for n, c in tasks))
    for name, status in results:
        checks[name] = status
    return checks


@router.get("/healthz")
async def healthz() -> JSONResponse:
    settings = get_settings()
    checks = await _run_checks(settings)

    overall = "ok"
    for status in checks.values():
        if status == "unhealthy":
            overall = "degraded"
            break

    body = HealthResponse(
        status=overall,
        version=__version__,
        environment=settings.env.value,
        checks=checks,
    )
    status_code = 503 if overall == "degraded" else 200
    return JSONResponse(content=body.model_dump(), status_code=status_code)


@router.get("/metrics")
async def metrics() -> Response:
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
