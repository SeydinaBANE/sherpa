from __future__ import annotations

from dataclasses import dataclass, field

from app.infrastructure.llm.anthropic import AnthropicLLM


@dataclass
class _Block:
    text: str


@dataclass
class _Reply:
    content: list[_Block]


@dataclass
class _Messages:
    calls: list[dict[str, object]] = field(default_factory=list)

    async def create(
        self,
        *,
        model: str,
        max_tokens: int,
        system: str,
        messages: list[dict[str, str]],
    ) -> _Reply:
        self.calls.append({"model": model, "max_tokens": max_tokens, "messages": messages})
        return _Reply(content=[_Block("Bonjour"), _Block(" monde")])


@dataclass
class _Client:
    messages: _Messages = field(default_factory=_Messages)


async def test_anthropic_llm_concatenates_blocks_and_passes_model() -> None:
    client = _Client()
    llm = AnthropicLLM(api_key="x", client=client)
    text = await llm.complete(
        system="sys", prompt="question", model="claude-sonnet-4-6", max_tokens=128
    )
    assert text == "Bonjour monde"
    assert client.messages.calls[0]["model"] == "claude-sonnet-4-6"
