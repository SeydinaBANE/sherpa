from __future__ import annotations

import asyncio
import sys

from app.application.ingestion.chunker import chunk_document
from app.application.rag.prompts import build_context_block
from app.application.rag.service import RagService
from app.config import LLMBackend, get_settings
from app.domain.ports import LLMPort
from app.infrastructure.retrieval.in_memory import InMemoryRetriever
from app.presentation.dependencies import get_llm

from evals.dataset import GOLDEN_SET, EvalCase
from evals.judge import LLMJudge

SCORE_THRESHOLD = 4.0
TOP_K = 4


async def _judge_case(case: EvalCase, llm: LLMPort, judge: LLMJudge, model: str) -> int:
    retriever = InMemoryRetriever()
    await retriever.index(chunk_document(case.course_id, case.source, case.document))
    answer = await RagService(retriever, llm, model, 512, top_k=TOP_K).answer(
        case.course_id, case.question
    )
    context = build_context_block(await retriever.retrieve(case.course_id, case.question, TOP_K))
    verdict = await judge.judge(case.question, answer.text, context)
    return verdict.score


async def main() -> int:
    settings = get_settings()
    if settings.llm_backend is not LLMBackend.ANTHROPIC:
        sys.stdout.write("LLM-judge ignoré (backend non-anthropic).\n")
        return 0
    llm = get_llm()
    judge = LLMJudge(llm, settings.llm_model_deep)
    scores = [
        await _judge_case(case, llm, judge, settings.llm_model_standard) for case in GOLDEN_SET
    ]
    average = sum(scores) / len(scores)
    sys.stdout.write(f"judge_avg_score={average:.2f} n={len(scores)}\n")
    if average < SCORE_THRESHOLD:
        sys.stdout.write("JUDGE FAILED: score moyen sous le seuil\n")
        return 1
    sys.stdout.write("JUDGE PASSED\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
