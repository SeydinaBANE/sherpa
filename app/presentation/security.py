from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from app.config import get_settings
from app.infrastructure.ratelimit.in_memory import FixedWindowRateLimiter
from app.infrastructure.ratelimit.quota import DailyRequestQuota
from app.presentation.dependencies import get_rate_limiter, get_request_quota


async def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    settings = get_settings()
    if not settings.auth_enabled:
        return
    if x_api_key is None or x_api_key not in settings.api_key_set:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante",
            headers={"WWW-Authenticate": "ApiKey"},
        )


def _client_identity(request: Request, api_key: str | None) -> str:
    if api_key:
        return f"key:{api_key}"
    client = request.client
    return f"ip:{client.host}" if client is not None else "anon"


async def rate_limit(
    request: Request,
    limiter: Annotated[FixedWindowRateLimiter, Depends(get_rate_limiter)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return
    if not limiter.allow(_client_identity(request, x_api_key)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de requêtes, réessayez plus tard",
        )


async def enforce_quota(
    request: Request,
    quota: Annotated[DailyRequestQuota, Depends(get_request_quota)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    settings = get_settings()
    if not settings.quota_enabled:
        return
    if not quota.allow(_client_identity(request, x_api_key)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota journalier dépassé",
        )
