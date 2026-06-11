from __future__ import annotations

from pydantic import BaseModel


class EvalCase(BaseModel):
    course_id: str
    source: str
    document: str
    question: str
    expected_keywords: tuple[str, ...]


GOLDEN_SET: tuple[EvalCase, ...] = (
    EvalCase(
        course_id="bio",
        source="bio.pdf",
        document=(
            "La photosynthèse transforme la lumière en énergie chimique dans les chloroplastes."
        ),
        question="Où se déroule la photosynthèse ?",
        expected_keywords=("chloroplastes",),
    ),
    EvalCase(
        course_id="histoire",
        source="histoire.pdf",
        document="La Révolution française débute en 1789 avec la prise de la Bastille.",
        question="En quelle année débute la Révolution française ?",
        expected_keywords=("1789",),
    ),
)
