from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.entities import Answer


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class IngestRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    source: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1)


class IngestResponse(BaseModel):
    course_id: str
    chunks_created: int


class AskRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=2000)


class CitationResponse(BaseModel):
    source: str
    ordinal: int
    snippet: str


class AskResponse(BaseModel):
    answer: str
    model: str
    grounded: bool
    citations: list[CitationResponse]

    @classmethod
    def from_domain(cls, answer: Answer) -> AskResponse:
        return cls(
            answer=answer.text,
            model=answer.model,
            grounded=answer.is_grounded,
            citations=[
                CitationResponse(source=c.source, ordinal=c.ordinal, snippet=c.snippet)
                for c in answer.citations
            ],
        )
