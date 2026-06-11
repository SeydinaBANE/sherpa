from __future__ import annotations

import math
import re
from collections import defaultdict

from app.domain.entities import Chunk, RetrievedChunk

_TOKEN = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class InMemoryRetriever:
    """Retriever lexical (TF-IDF cosine) — adapter par défaut, testable hors-ligne.

    Implémente RetrieverPort. Remplaçable par un adapter Qdrant + embeddings
    sans toucher au domaine ni à l'application (inversion de dépendance).
    """

    def __init__(self) -> None:
        self._by_course: dict[str, list[Chunk]] = defaultdict(list)
        self._known_ids: set[str] = set()

    async def index(self, chunks: list[Chunk]) -> int:
        added = 0
        for chunk in chunks:
            if chunk.chunk_id in self._known_ids:
                continue
            self._by_course[chunk.course_id].append(chunk)
            self._known_ids.add(chunk.chunk_id)
            added += 1
        return added

    async def delete_course(self, course_id: str) -> int:
        chunks = self._by_course.pop(course_id, [])
        for chunk in chunks:
            self._known_ids.discard(chunk.chunk_id)
        return len(chunks)

    async def retrieve(self, course_id: str, query: str, top_k: int) -> list[RetrievedChunk]:
        corpus = self._by_course.get(course_id, [])
        if not corpus:
            return []
        query_tokens = set(_tokenize(query))
        if not query_tokens:
            return []
        idf = self._inverse_document_frequency(corpus)
        scored = [
            RetrievedChunk(chunk=chunk, score=score)
            for chunk in corpus
            if (score := self._score(chunk.text, query_tokens, idf)) > 0.0
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _inverse_document_frequency(corpus: list[Chunk]) -> dict[str, float]:
        document_frequency: dict[str, int] = defaultdict(int)
        for chunk in corpus:
            for token in set(_tokenize(chunk.text)):
                document_frequency[token] += 1
        total = len(corpus)
        return {token: math.log(1 + total / count) for token, count in document_frequency.items()}

    @staticmethod
    def _score(text: str, query_tokens: set[str], idf: dict[str, float]) -> float:
        tokens = _tokenize(text)
        if not tokens:
            return 0.0
        frequency: dict[str, int] = defaultdict(int)
        for token in tokens:
            frequency[token] += 1
        return sum(frequency[token] * idf.get(token, 0.0) for token in query_tokens) / len(tokens)
