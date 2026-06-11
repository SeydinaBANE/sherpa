from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.embeddings.voyage import VoyageEmbedding


@dataclass
class _Result:
    embeddings: list[list[float]]


class _Client:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str, str]] = []

    def embed(self, texts: list[str], *, model: str, input_type: str) -> _Result:
        self.calls.append((texts, model, input_type))
        return _Result(embeddings=[[0.1, 0.2] for _ in texts])


async def test_voyage_embedding_returns_vectors_and_uses_model() -> None:
    client = _Client()
    embedding = VoyageEmbedding(api_key="x", model="voyage-3", client=client)
    vectors = await embedding.embed(["a", "b"])
    assert vectors == [[0.1, 0.2], [0.1, 0.2]]
    assert client.calls[0][1] == "voyage-3"
    assert client.calls[0][2] == "document"
