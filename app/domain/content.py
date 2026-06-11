from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChunkRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str
    source: str
    ordinal: int
    created_at: datetime
