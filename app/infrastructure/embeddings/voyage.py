from __future__ import annotations

import asyncio
from typing import Protocol, cast


class _VoyageResult(Protocol):
    embeddings: list[list[float]]


class _VoyageClient(Protocol):
    def embed(self, texts: list[str], *, model: str, input_type: str) -> _VoyageResult: ...


class VoyageEmbedding:
    """Adapter Voyage AI implémentant EmbeddingPort. Import lazy, client injectable."""

    def __init__(
        self,
        api_key: str,
        model: str,
        client: _VoyageClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = client

    def _get_client(self) -> _VoyageClient:
        if self._client is None:
            import voyageai

            self._client = cast(_VoyageClient, voyageai.Client(api_key=self._api_key))
        return self._client

    async def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        result = await asyncio.to_thread(
            lambda: client.embed(texts, model=self._model, input_type="document")
        )
        return result.embeddings
