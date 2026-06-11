from __future__ import annotations

import re

_CONTEXT_LINE = re.compile(r"^\[(?P<source>[^:]+):(?P<ordinal>\d+)\]\s*(?P<text>.+)$")


class EchoLLM:
    """LLM déterministe hors-ligne — adapter par défaut implémentant LLMPort.

    Construit une réponse citée à partir du contexte, sans appel réseau.
    Remplaçable par AnthropicLLM (Claude) via l'extra `rag` en production.
    """

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        sentences = self._extract_context(prompt)
        if not sentences:
            return "Le contexte fourni ne permet pas de répondre à cette question."
        body = " ".join(
            f"D'après [{source}:{ordinal}], {text}" for source, ordinal, text in sentences[:2]
        )
        return body[: max_tokens * 4]

    @staticmethod
    def _extract_context(prompt: str) -> list[tuple[str, int, str]]:
        out: list[tuple[str, int, str]] = []
        for line in prompt.splitlines():
            match = _CONTEXT_LINE.match(line.strip())
            if match is None:
                continue
            snippet = match.group("text").strip()
            out.append((match.group("source"), int(match.group("ordinal")), snippet))
        return out
