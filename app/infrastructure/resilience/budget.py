from __future__ import annotations

from collections.abc import Callable
from datetime import date

from app.domain.exceptions import BudgetExceededError


class DailyTokenBudget:
    """Garde-fou de coût : plafonne les tokens consommés par jour."""

    def __init__(self, daily_budget: int, today: Callable[[], date] = date.today) -> None:
        if daily_budget <= 0:
            raise ValueError("daily_budget must be positive")
        self._daily_budget = daily_budget
        self._today = today
        self._day: date | None = None
        self._used = 0

    def charge(self, tokens: int) -> None:
        current_day = self._today()
        if current_day != self._day:
            self._day = current_day
            self._used = 0
        projected = self._used + tokens
        if projected > self._daily_budget:
            raise BudgetExceededError(projected, self._daily_budget)
        self._used = projected
