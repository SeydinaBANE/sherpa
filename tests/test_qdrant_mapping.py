from __future__ import annotations

import uuid

from app.domain.entities import Chunk
from app.infrastructure.retrieval.qdrant import from_payload, point_id, to_payload


def test_payload_round_trip_preserves_chunk() -> None:
    chunk = Chunk.create("c1", "bio.pdf", 3, "La photosynthèse.")
    payload = to_payload(chunk)
    retrieved = from_payload(payload, score=0.42)
    assert retrieved.chunk == chunk
    assert retrieved.score == 0.42


def test_point_id_is_deterministic_uuid() -> None:
    first = point_id("abc")
    second = point_id("abc")
    assert first == second
    assert uuid.UUID(first).version == 5
