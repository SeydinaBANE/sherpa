from __future__ import annotations

import pytest
from app.application.agents.intent import Intent, classify_intent


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Donne-moi un quiz sur la photosynthèse", Intent.QUIZ),
        ("Fais un plan de révision pour l'examen", Intent.PLAN),
        ("Explique la photosynthèse", Intent.TUTOR),
    ],
)
def test_classify_intent(message: str, expected: Intent) -> None:
    assert classify_intent(message) is expected
