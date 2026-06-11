from __future__ import annotations

from pathlib import Path

_TEXT_SUFFIXES = {".txt", ".md"}


def load_text(path: Path) -> str:
    return load_bytes(path.name, path.read_bytes())


def load_bytes(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in _TEXT_SUFFIXES:
        return data.decode("utf-8")
    if suffix == ".pdf":
        return _load_pdf_bytes(data)
    raise ValueError(f"Type de fichier non supporté: {suffix}")


def _load_pdf_bytes(data: bytes) -> str:
    import fitz

    with fitz.open(stream=data, filetype="pdf") as document:
        return "\n\n".join(page.get_text() for page in document)
