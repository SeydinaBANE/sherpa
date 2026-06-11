from __future__ import annotations

from pydantic import BaseModel

from app.application.rag.prompts import build_context_block
from app.domain.agents import Quiz, QuizQuestion
from app.domain.ports import LLMPort, RetrieverPort

from .base import parse_model, retrieve_context
from .prompts import QUIZ_SYSTEM, quiz_prompt


class _QuestionPayload(BaseModel):
    question: str
    choices: list[str]
    answer_index: int
    explanation: str


class _QuizPayload(BaseModel):
    questions: list[_QuestionPayload]


class QuizGenerator:
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

    async def generate(self, course_id: str, topic: str, num_questions: int) -> Quiz:
        retrieved = await retrieve_context(self._retriever, course_id, topic, self._top_k)
        prompt = quiz_prompt(build_context_block(retrieved), topic, num_questions)
        text = await self._llm.complete(
            system=QUIZ_SYSTEM, prompt=prompt, model=self._model, max_tokens=self._max_tokens
        )
        payload = parse_model(text, _QuizPayload)
        questions = tuple(
            QuizQuestion(
                question=item.question,
                choices=tuple(item.choices),
                answer_index=item.answer_index,
                explanation=item.explanation,
            )
            for item in payload.questions
        )
        return Quiz(course_id=course_id, topic=topic, questions=questions)
