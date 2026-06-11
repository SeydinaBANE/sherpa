from __future__ import annotations

from pathlib import Path

_TEXT_SUFFIXES = {".txt", ".md"}


def load_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Type de fichier non supporté: {suffix}")


def _load_pdf(path: Path) -> str:
    import fitz

    with fitz.open(path) as document:
        return "\n\n".join(page.get_text() for page in document)
