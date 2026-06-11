from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.domain.ports import ChunkMetadataPort, RetrieverPort
from app.presentation.dependencies import get_chunk_store, get_retriever
from app.presentation.schemas_courses import (
    ChunkRefResponse,
    CourseChunksResponse,
    DeleteCourseResponse,
)

router = APIRouter(prefix="/courses", tags=["courses"])

_CourseId = Annotated[str, Path(min_length=1, max_length=128)]


@router.get("/{course_id}/chunks", response_model=CourseChunksResponse)
async def list_chunks(
    course_id: _CourseId,
    store: Annotated[ChunkMetadataPort, Depends(get_chunk_store)],
) -> CourseChunksResponse:
    refs = await store.list_by_course(course_id)
    return CourseChunksResponse(
        course_id=course_id,
        chunks=[ChunkRefResponse.from_domain(ref) for ref in refs],
    )


@router.delete("/{course_id}", response_model=DeleteCourseResponse)
async def delete_course(
    course_id: _CourseId,
    store: Annotated[ChunkMetadataPort, Depends(get_chunk_store)],
    retriever: Annotated[RetrieverPort, Depends(get_retriever)],
) -> DeleteCourseResponse:
    vectors_deleted = await retriever.delete_course(course_id)
    chunks_deleted = await store.delete_course(course_id)
    return DeleteCourseResponse(
        course_id=course_id,
        vectors_deleted=vectors_deleted,
        chunks_deleted=chunks_deleted,
    )
