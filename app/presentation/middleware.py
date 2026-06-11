from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response

from app.infrastructure.observability.logging import get_logger
from app.infrastructure.observability.metrics import observe_request

_logger = get_logger("http")

RequestHandler = Callable[[Request], Awaitable[Response]]


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else request.url.path


async def observability_middleware(request: Request, call_next: RequestHandler) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)
    method = request.method
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start
        observe_request(method, request.url.path, 500, duration)
        _logger.exception("request_failed", method=method, path=request.url.path)
        structlog.contextvars.unbind_contextvars("request_id")
        raise
    duration = time.perf_counter() - start
    path = _route_path(request)
    observe_request(method, path, response.status_code, duration)
    response.headers["X-Request-ID"] = request_id
    _logger.info(
        "request",
        method=method,
        path=path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    structlog.contextvars.unbind_contextvars("request_id")
    return response
