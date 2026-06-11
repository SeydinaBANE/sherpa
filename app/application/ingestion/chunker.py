from __future__ import annotations

import re

from app.domain.entities import Chunk

_PARAGRAPH = re.compile(r"\n\s*\n")
_WHITESPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def split_text(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    paragraphs = [_normalize(p) for p in _PARAGRAPH.split(text) if _normalize(p)]
    chunks: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = f"{buffer} {paragraph}".strip() if buffer else paragraph
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        if len(paragraph) <= max_chars:
            buffer = paragraph
        else:
            chunks.extend(paragraph[i : i + max_chars] for i in range(0, len(paragraph), max_chars))
            buffer = ""
    if buffer:
        chunks.append(buffer)
    return chunks


def chunk_document(course_id: str, source: str, text: str, max_chars: int = 1200) -> list[Chunk]:
    return [
        Chunk.create(course_id=course_id, source=source, ordinal=ordinal, text=piece)
        for ordinal, piece in enumerate(split_text(text, max_chars))
    ]
