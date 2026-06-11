from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version=__version__, environment=settings.env.value)
