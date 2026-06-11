from __future__ import annotations

import pytest
from app.domain.exceptions import AgentOutputError
from evals.judge import JudgeVerdict, LLMJudge


class _FakeJudgeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.last_prompt = ""

    async def complete(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        self.last_prompt = prompt
        return self._reply


async def test_judge_parses_valid_verdict() -> None:
    reply = '{"faithful": true, "score": 5, "rationale": "réponse fidèle au contexte"}'
    judge = LLMJudge(_FakeJudgeLLM(reply), model="m")
    verdict = await judge.judge("Q ?", "réponse", "contexte")
    assert isinstance(verdict, JudgeVerdict)
    assert verdict.faithful is True
    assert verdict.score == 5


async def test_judge_rejects_invalid_json() -> None:
    judge = LLMJudge(_FakeJudgeLLM("pas du json"), model="m")
    with pytest.raises(AgentOutputError):
        await judge.judge("Q ?", "réponse", "contexte")


async def test_judge_rejects_out_of_range_score() -> None:
    judge = LLMJudge(_FakeJudgeLLM('{"faithful": true, "score": 9, "rationale": "x"}'), model="m")
    with pytest.raises(AgentOutputError):
        await judge.judge("Q ?", "réponse", "contexte")
