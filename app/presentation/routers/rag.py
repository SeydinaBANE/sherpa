from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.application.ingestion.chunker import chunk_document
from app.application.ingestion.loaders import load_bytes
from app.application.rag.service import RagService
from app.presentation.dependencies import get_chunk_store, get_rag_service, get_retriever
from app.presentation.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
)

router = APIRouter(tags=["rag"])


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(request: IngestRequest) -> IngestResponse:
    chunks = chunk_document(request.course_id, request.source, request.text)
    created = await get_retriever().index(chunks)
    await get_chunk_store().record(chunks)
    return IngestResponse(course_id=request.course_id, chunks_created=created)


@router.post("/ingest/file", response_model=IngestResponse, status_code=201)
async def ingest_file(
    course_id: Annotated[str, Form(min_length=1, max_length=128)],
    file: Annotated[UploadFile, File()],
) -> IngestResponse:
    filename = file.filename or "upload"
    data = await file.read()
    try:
        text = load_bytes(filename, data)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    chunks = chunk_document(course_id, filename, text)
    created = await get_retriever().index(chunks)
    await get_chunk_store().record(chunks)
    return IngestResponse(course_id=course_id, chunks_created=created)


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> AskResponse:
    answer = await service.answer(request.course_id, request.question)
    return AskResponse.from_domain(answer)
