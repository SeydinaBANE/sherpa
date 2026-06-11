from __future__ import annotations

from enum import StrEnum


class Intent(StrEnum):
    TUTOR = "tutor"
    QUIZ = "quiz"
    PLAN = "plan"


_QUIZ_KEYWORDS = ("quiz", "qcm", "question", "interroge", "teste", "exercice")
_PLAN_KEYWORDS = ("plan", "planning", "programme", "révision", "reviser", "réviser", "calendrier")


def classify_intent(message: str) -> Intent:
    lowered = message.lower()
    if any(keyword in lowered for keyword in _QUIZ_KEYWORDS):
        return Intent.QUIZ
    if any(keyword in lowered for keyword in _PLAN_KEYWORDS):
        return Intent.PLAN
    return Intent.TUTOR
