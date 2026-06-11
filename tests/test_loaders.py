from __future__ import annotations

from pathlib import Path

import pytest
from app.application.ingestion.loaders import load_bytes, load_text


def test_load_text_reads_txt(tmp_path: Path) -> None:
    file = tmp_path / "cours.txt"
    file.write_text("Bonjour le monde.", encoding="utf-8")
    assert load_text(file) == "Bonjour le monde."


def test_load_text_reads_markdown(tmp_path: Path) -> None:
    file = tmp_path / "notes.md"
    file.write_text("# Titre", encoding="utf-8")
    assert load_text(file) == "# Titre"


def test_load_text_rejects_unsupported_suffix(tmp_path: Path) -> None:
    file = tmp_path / "image.png"
    file.write_bytes(b"\x89PNG")
    with pytest.raises(ValueError, match="non supporté"):
        load_text(file)


def test_load_bytes_decodes_text() -> None:
    assert load_bytes("notes.txt", b"Bonjour") == "Bonjour"


def test_load_bytes_rejects_unsupported_suffix() -> None:
    with pytest.raises(ValueError, match="non supporté"):
        load_bytes("image.png", b"\x89PNG")
