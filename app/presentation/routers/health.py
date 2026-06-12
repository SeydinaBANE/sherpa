from __future__ import annotations

import asyncio

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app import __version__
from app.config import CacheBackend, MemoryBackend, RetrievalBackend, get_settings
from app.infrastructure.observability.metrics import render_metrics
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> JSONResponse:
    settings = get_settings()
    checks: dict[str, str] = {}

    if settings.memory_backend is MemoryBackend.SQL:
        try:
            from sqlalchemy import text

            from app.infrastructure.persistence.engine import create_engine as _ce

            engine = _ce(settings.database_url)
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unhealthy"

    if settings.cache_backend is CacheBackend.REDIS:
        try:
            from redis.asyncio import Redis as _AsyncRedis

            r = _AsyncRedis.from_url(settings.redis_url)
            await r.ping()
            await r.aclose()
            checks["cache"] = "ok"
        except Exception:
            checks["cache"] = "unhealthy"

    if settings.retrieval_backend is RetrievalBackend.HYBRID:
        try:
            from qdrant_client import QdrantClient

            _client = QdrantClient(url=settings.qdrant_url)
            await asyncio.to_thread(_client.get_collections)
            checks["vector_store"] = "ok"
        except Exception:
            checks["vector_store"] = "unhealthy"

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
