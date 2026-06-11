from __future__ import annotations

from fastapi import APIRouter, Response

from app import __version__
from app.config import get_settings
from app.infrastructure.observability.metrics import render_metrics
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version=__version__, environment=settings.env.value)


@router.get("/metrics")
async def metrics() -> Response:
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
