from __future__ import annotations

from app.application.agents.base import parse_model
from app.domain.ports import LLMPort
from pydantic import BaseModel, Field

JUDGE_SYSTEM = (
    "Tu es un évaluateur rigoureux. Évalue si la RÉPONSE est fidèle au CONTEXTE et "
    "répond à la QUESTION. Ne réponds qu'en JSON valide, sans texte autour. "
    'Schéma: {"faithful":bool,"score":int,"rationale":str} où score est de 1 à 5.'
)


class JudgeVerdict(BaseModel):
    faithful: bool
    score: int = Field(ge=1, le=5)
    rationale: str


def _judge_prompt(question: str, answer: str, context: str) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"RÉPONSE:\n{answer}\n\n"
        "Évalue la fidélité. JSON uniquement."
    )


class LLMJudge:
    """Évalue la qualité d'une réponse RAG via un LLM (LLM-as-a-judge)."""

    def __init__(self, llm: LLMPort, model: str, max_tokens: int = 512) -> None:
        self._llm = llm
        self._model = model
        self._max_tokens = max_tokens

    async def judge(self, question: str, answer: str, context: str) -> JudgeVerdict:
        text = await self._llm.complete(
            system=JUDGE_SYSTEM,
            prompt=_judge_prompt(question, answer, context),
            model=self._model,
            max_tokens=self._max_tokens,
        )
        return parse_model(text, JudgeVerdict)
