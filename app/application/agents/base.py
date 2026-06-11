from __future__ import annotations

import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.domain.entities import RetrievedChunk
from app.domain.exceptions import AgentOutputError, NoRelevantContextError
from app.domain.ports import RetrieverPort

T = TypeVar("T", bound=BaseModel)

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def parse_model(text: str, model: type[T]) -> T:
    candidate = text.strip()
    match = _FENCE.search(candidate)
    if match:
        candidate = match.group(1).strip()
    try:
        return model.model_validate_json(candidate)
    except ValidationError as exc:
        raise AgentOutputError(str(exc)) from exc


async def retrieve_context(
    retriever: RetrieverPort,
    course_id: str,
    query: str,
    top_k: int,
) -> list[RetrievedChunk]:
    retrieved = await retriever.retrieve(course_id, query, top_k)
    if not retrieved:
        raise NoRelevantContextError(query)
    return retrieved
