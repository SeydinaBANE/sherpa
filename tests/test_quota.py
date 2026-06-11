from __future__ import annotations

from datetime import date

from app.infrastructure.ratelimit.quota import DailyRequestQuota


def test_quota_allows_up_to_limit_then_blocks() -> None:
    quota = DailyRequestQuota(limit=2, today=lambda: date(2026, 1, 1))
    assert quota.allow("k") is True
    assert quota.allow("k") is True
    assert quota.allow("k") is False


def test_quota_resets_on_new_day() -> None:
    days = {"d": date(2026, 1, 1)}
    quota = DailyRequestQuota(limit=1, today=lambda: days["d"])
    assert quota.allow("k") is True
    assert quota.allow("k") is False
    days["d"] = date(2026, 1, 2)
    assert quota.allow("k") is True


def test_quota_isolates_identities() -> None:
    quota = DailyRequestQuota(limit=1, today=lambda: date(2026, 1, 1))
    assert quota.allow("a") is True
    assert quota.allow("b") is True
    assert quota.allow("a") is False
