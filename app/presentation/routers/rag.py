from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.ingestion.chunker import chunk_document
from app.application.rag.service import RagService
from app.presentation.dependencies import get_rag_service, get_retriever
from app.presentation.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
)

router = APIRouter(tags=["rag"])


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(request: IngestRequest) -> IngestResponse:
    retriever = get_retriever()
    chunks = chunk_document(request.course_id, request.source, request.text)
    created = await retriever.index(chunks)
    return IngestResponse(course_id=request.course_id, chunks_created=created)


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> AskResponse:
    answer = await service.answer(request.course_id, request.question)
    return AskResponse.from_domain(answer)
