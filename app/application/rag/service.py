from __future__ import annotations

from app.domain.entities import Answer, Citation, RetrievedChunk
from app.domain.exceptions import NoRelevantContextError
from app.domain.ports import LLMPort, RetrieverPort

from .prompts import SYSTEM_PROMPT, build_user_prompt

_SNIPPET_CHARS = 160


def _to_citations(retrieved: list[RetrievedChunk]) -> tuple[Citation, ...]:
    return tuple(
        Citation(
            source=item.chunk.source,
            ordinal=item.chunk.ordinal,
            snippet=item.chunk.text[:_SNIPPET_CHARS],
        )
        for item in retrieved
    )


class RagService:
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

    async def answer(self, course_id: str, question: str) -> Answer:
        retrieved = await self._retriever.retrieve(course_id, question, self._top_k)
        if not retrieved:
            raise NoRelevantContextError(question)
        prompt = build_user_prompt(question, retrieved)
        text = await self._llm.complete(
            system=SYSTEM_PROMPT,
            prompt=prompt,
            model=self._model,
            max_tokens=self._max_tokens,
        )
        return Answer(
            question=question,
            course_id=course_id,
            text=text,
            citations=_to_citations(retrieved),
            model=self._model,
        )
