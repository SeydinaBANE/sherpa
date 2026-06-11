from __future__ import annotations

import asyncio
import sys

from app.application.ingestion.chunker import chunk_document
from app.application.rag.service import RagService
from app.infrastructure.llm.echo import EchoLLM
from app.infrastructure.retrieval.in_memory import InMemoryRetriever

from evals.dataset import GOLDEN_SET, EvalCase

GROUNDING_THRESHOLD = 1.0
KEYWORD_THRESHOLD = 0.5


async def _evaluate_case(case: EvalCase) -> tuple[bool, bool]:
    retriever = InMemoryRetriever()
    await retriever.index(chunk_document(case.course_id, case.source, case.document))
    service = RagService(retriever=retriever, llm=EchoLLM(), model="eval-stub", max_tokens=512)
    answer = await service.answer(case.course_id, case.question)
    grounded = answer.is_grounded
    keyword_hit = any(kw.lower() in answer.text.lower() for kw in case.expected_keywords)
    return grounded, keyword_hit


async def main() -> int:
    results = [await _evaluate_case(case) for case in GOLDEN_SET]
    total = len(results)
    grounding = sum(1 for grounded, _ in results if grounded) / total
    keyword = sum(1 for _, hit in results if hit) / total
    sys.stdout.write(f"grounding={grounding:.2f} keyword_recall={keyword:.2f} n={total}\n")
    if grounding < GROUNDING_THRESHOLD or keyword < KEYWORD_THRESHOLD:
        sys.stdout.write("EVALS FAILED: seuils non atteints\n")
        return 1
    sys.stdout.write("EVALS PASSED\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
