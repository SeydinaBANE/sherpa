from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.config import get_settings
from app.domain.exceptions import (
    AgentOutputError,
    BudgetExceededError,
    CourseNotFoundError,
    NoRelevantContextError,
)
from app.infrastructure.observability.logging import configure_logging
from app.presentation.routers import agents, assistant, health, memory, rag


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NoRelevantContextError)
    async def _no_context(_: Request, exc: NoRelevantContextError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(CourseNotFoundError)
    async def _not_found(_: Request, exc: CourseNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(BudgetExceededError)
    async def _budget(_: Request, exc: BudgetExceededError) -> JSONResponse:
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @app.exception_handler(AgentOutputError)
    async def _agent_output(_: Request, exc: AgentOutputError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title="Sherpa",
        version=__version__,
        description="Tuteur IA pour la préparation d'examens (RAG + agents).",
    )
    app.include_router(health.router)
    app.include_router(rag.router)
    app.include_router(agents.router)
    app.include_router(assistant.router)
    app.include_router(memory.router)
    _register_exception_handlers(app)
    return app
