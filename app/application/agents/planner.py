from __future__ import annotations

from pydantic import BaseModel

from app.application.rag.prompts import build_context_block
from app.domain.agents import StudyPlan, StudyPlanItem
from app.domain.ports import LLMPort, RetrieverPort

from .base import parse_model, retrieve_context
from .prompts import PLAN_SYSTEM, plan_prompt


class _ItemPayload(BaseModel):
    day: int
    topic: str
    activities: list[str]


class _PlanPayload(BaseModel):
    items: list[_ItemPayload]


class StudyPlanner:
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

    async def generate(self, course_id: str, topic: str, days: int) -> StudyPlan:
        retrieved = await retrieve_context(self._retriever, course_id, topic, self._top_k)
        prompt = plan_prompt(build_context_block(retrieved), topic, days)
        text = await self._llm.complete(
            system=PLAN_SYSTEM, prompt=prompt, model=self._model, max_tokens=self._max_tokens
        )
        payload = parse_model(text, _PlanPayload)
        items = tuple(
            StudyPlanItem(day=item.day, topic=item.topic, activities=tuple(item.activities))
            for item in payload.items
        )
        return StudyPlan(course_id=course_id, items=items)
