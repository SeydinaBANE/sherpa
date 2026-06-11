from __future__ import annotations

import uuid
from typing import Protocol, cast

from app.domain.entities import Chunk, RetrievedChunk
from app.domain.ports import EmbeddingPort

Payload = dict[str, str | int]


class _ScoredPoint(Protocol):
    score: float
    payload: Payload | None


class _QdrantClient(Protocol):
    def collection_exists(self, collection_name: str) -> bool: ...

    def create_collection(self, collection_name: str, vectors_config: object) -> object: ...

    def upsert(self, collection_name: str, points: object) -> object: ...

    def delete(self, collection_name: str, points_selector: object) -> object: ...

    def search(
        self,
        *,
        collection_name: str,
        query_vector: list[float],
        query_filter: object,
        limit: int,
    ) -> list[_ScoredPoint]: ...


def to_payload(chunk: Chunk) -> Payload:
    return {
        "chunk_id": chunk.chunk_id,
        "course_id": chunk.course_id,
        "source": chunk.source,
        "ordinal": chunk.ordinal,
        "text": chunk.text,
    }


def from_payload(payload: Payload, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        chunk=Chunk(
            chunk_id=str(payload["chunk_id"]),
            course_id=str(payload["course_id"]),
            source=str(payload["source"]),
            ordinal=int(payload["ordinal"]),
            text=str(payload["text"]),
        ),
        score=score,
    )


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


class QdrantRetriever:
    """Adapter Qdrant (dense) implémentant RetrieverPort. Import lazy, client injectable."""

    def __init__(
        self,
        url: str,
        collection: str,
        embeddings: EmbeddingPort,
        client: _QdrantClient | None = None,
    ) -> None:
        self._url = url
        self._collection = collection
        self._embeddings = embeddings
        self._client = client

    def _get_client(self) -> _QdrantClient:
        if self._client is None:
            from qdrant_client import QdrantClient

            self._client = cast(_QdrantClient, QdrantClient(url=self._url))
        return self._client

    def _ensure_collection(self, dimension: int) -> None:
        client = self._get_client()
        if client.collection_exists(self._collection):
            return
        from qdrant_client import models as qmodels

        client.create_collection(
            self._collection,
            vectors_config=qmodels.VectorParams(size=dimension, distance=qmodels.Distance.COSINE),
        )

    async def index(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        vectors = await self._embeddings.embed([chunk.text for chunk in chunks])
        self._ensure_collection(len(vectors[0]))
        from qdrant_client import models as qmodels

        points = [
            qmodels.PointStruct(
                id=point_id(chunk.chunk_id), vector=vector, payload=to_payload(chunk)
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self._get_client().upsert(collection_name=self._collection, points=points)
        return len(points)

    @staticmethod
    def _course_filter(course_id: str) -> object:
        from qdrant_client import models as qmodels

        return qmodels.Filter(
            must=[
                qmodels.FieldCondition(key="course_id", match=qmodels.MatchValue(value=course_id))
            ]
        )

    async def delete_course(self, course_id: str) -> int:
        self._get_client().delete(
            collection_name=self._collection,
            points_selector=self._course_filter(course_id),
        )
        return 0

    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]:
        vectors = await self._embeddings.embed([query])
        query_filter = self._course_filter(course_id)
        points = self._get_client().search(
            collection_name=self._collection,
            query_vector=vectors[0],
            query_filter=query_filter,
            limit=top_k,
        )
        return [
            from_payload(point.payload, point.score)
            for point in points
            if point.payload is not None
        ]
