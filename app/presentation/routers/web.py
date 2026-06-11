from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

_INDEX = Path(__file__).resolve().parent.parent / "static" / "index.html"

router = APIRouter(tags=["web"])


@router.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(_INDEX, media_type="text/html")
