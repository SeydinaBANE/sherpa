from __future__ import annotations

from app.domain.entities import RetrievedChunk

SYSTEM_PROMPT = (
    "Tu es Sherpa, un tuteur pédagogique. Réponds uniquement à partir du CONTEXTE fourni. "
    "Si le contexte ne contient pas la réponse, dis-le explicitement sans inventer. "
    "Cite tes sources en référençant [source:ordinal]. Réponds en français, de façon claire."
)


def build_context_block(retrieved: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[{item.chunk.source}:{item.chunk.ordinal}] {item.chunk.text}" for item in retrieved
    )


def build_user_prompt(question: str, retrieved: list[RetrievedChunk]) -> str:
    context = build_context_block(retrieved)
    return f"CONTEXTE:\n{context}\n\nQUESTION:\n{question}\n\nRÉPONSE:"
