from __future__ import annotations

import pytest
from app.application.ingestion.chunker import chunk_document, split_text


def test_split_text_groups_short_paragraphs() -> None:
    text = "Premier paragraphe.\n\nDeuxième paragraphe."
    chunks = split_text(text, max_chars=100)
    assert chunks == ["Premier paragraphe. Deuxième paragraphe."]


def test_split_text_splits_long_paragraph() -> None:
    chunks = split_text("a" * 250, max_chars=100)
    assert len(chunks) == 3
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_split_text_rejects_non_positive_max() -> None:
    with pytest.raises(ValueError, match="max_chars must be positive"):
        split_text("x", max_chars=0)


def test_chunk_document_is_deterministic() -> None:
    first = chunk_document("c1", "cours.pdf", "Bonjour le monde.")
    second = chunk_document("c1", "cours.pdf", "Bonjour le monde.")
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
