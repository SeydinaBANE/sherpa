from __future__ import annotations

from typing import Protocol, cast


class _ContentBlock(Protocol):
    text: str


class _Message(Protocol):
    content: list[_ContentBlock]


class _Messages(Protocol):
    async def create(
        self,
        *,
        model: str,
        max_tokens: int,
        system: str,
        messages: list[dict[str, str]],
    ) -> _Message: ...


class _AsyncAnthropic(Protocol):
    messages: _Messages


class AnthropicLLM:
    """Adapter Claude (async) implémentant LLMPort. Le modèle est choisi par appel (routing)."""

    def __init__(self, api_key: str, client: _AsyncAnthropic | None = None) -> None:
        self._api_key = api_key
        self._client = client

    def _get_client(self) -> _AsyncAnthropic:
        if self._client is None:
            import anthropic

            self._client = cast(_AsyncAnthropic, anthropic.AsyncAnthropic(api_key=self._api_key))
        return self._client

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        client = self._get_client()
        message = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content)
