from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.config import MemoryBackend, get_settings
from app.domain.exceptions import (
    AgentOutputError,
    BudgetExceededError,
    CourseNotFoundError,
    NoRelevantContextError,
)
from app.infrastructure.observability.logging import configure_logging, get_logger
from app.presentation.middleware import observability_middleware
from app.presentation.routers import (
    agents,
    assistant,
    courses,
    health,
    memory,
    rag,
    students,
    web,
)
from app.presentation.security import enforce_quota, rate_limit, require_api_key


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


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    log = get_logger("sherpa.startup")

    if settings.memory_backend is MemoryBackend.SQL:
        import alembic.command
        import alembic.config

        cfg = alembic.config.Config("alembic.ini")
        await asyncio.to_thread(alembic.command.upgrade, cfg, "head")
        log.info("database migrations applied")

    yield

    from app.presentation.dependencies import cleanup_backends

    await cleanup_backends()
    log.info("backends cleaned up")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title="Sherpa",
        version=__version__,
        description="Tuteur IA pour la préparation d'examens (RAG + agents).",
        lifespan=_lifespan,
    )
    app.middleware("http")(observability_middleware)
    protected = [Depends(require_api_key), Depends(rate_limit), Depends(enforce_quota)]
    app.include_router(web.router)
    app.include_router(health.router)
    app.include_router(rag.router, dependencies=protected)
    app.include_router(courses.router, dependencies=protected)
    app.include_router(agents.router, dependencies=protected)
    app.include_router(assistant.router, dependencies=protected)
    app.include_router(memory.router, dependencies=protected)
    app.include_router(students.router, dependencies=protected)
    _register_exception_handlers(app)
    return app
