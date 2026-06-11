from __future__ import annotations

from app.infrastructure.ratelimit.in_memory import FixedWindowRateLimiter


def test_rate_limiter_allows_up_to_limit_then_blocks() -> None:
    now = {"t": 0.0}
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=10, clock=lambda: now["t"])
    assert limiter.allow("k") is True
    assert limiter.allow("k") is True
    assert limiter.allow("k") is False


def test_rate_limiter_resets_on_new_window() -> None:
    now = {"t": 0.0}
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=10, clock=lambda: now["t"])
    assert limiter.allow("k") is True
    assert limiter.allow("k") is False
    now["t"] = 10.0
    assert limiter.allow("k") is True


def test_rate_limiter_isolates_identities() -> None:
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=10, clock=lambda: 0.0)
    assert limiter.allow("a") is True
    assert limiter.allow("b") is True
    assert limiter.allow("a") is False
