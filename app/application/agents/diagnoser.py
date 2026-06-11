from __future__ import annotations

from pydantic import BaseModel

from app.application.rag.prompts import build_context_block
from app.domain.agents import AnswerRecord, WeaknessReport
from app.domain.ports import LLMPort, RetrieverPort

from .base import parse_model, retrieve_context
from .prompts import DIAGNOSIS_SYSTEM, diagnosis_prompt


class _DiagnosisPayload(BaseModel):
    weak_topics: list[str]
    recommendation: str


def _answers_block(answers: list[AnswerRecord]) -> str:
    return "\n".join(
        f"- [{'OK' if record.correct else 'KO'}] {record.question}" for record in answers
    )


class WeaknessDiagnoser:
    def __init__(
        self,
        retriever: RetrieverPort,
        llm: LLMPort,
        model: str,
        max_tokens: int,
        top_k: int = 4,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._model = model
        self._max_tokens = max_tokens
        self._top_k = top_k

    async def diagnose(self, course_id: str, answers: list[AnswerRecord]) -> WeaknessReport:
        missed = " ".join(record.question for record in answers if not record.correct)
        query = missed or " ".join(record.question for record in answers)
        retrieved = await retrieve_context(self._retriever, course_id, query, self._top_k)
        prompt = diagnosis_prompt(build_context_block(retrieved), _answers_block(answers))
        text = await self._llm.complete(
            system=DIAGNOSIS_SYSTEM, prompt=prompt, model=self._model, max_tokens=self._max_tokens
        )
        payload = parse_model(text, _DiagnosisPayload)
        return WeaknessReport(
            course_id=course_id,
            weak_topics=tuple(payload.weak_topics),
            recommendation=payload.recommendation,
        )
