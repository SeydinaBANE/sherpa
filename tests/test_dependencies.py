from __future__ import annotations

from app.presentation import dependencies


def test_assistant_orchestrator_is_memoized() -> None:
    first = dependencies.get_assistant_orchestrator()
    second = dependencies.get_assistant_orchestrator()
    assert first is second


def test_singletons_share_instances() -> None:
    assert dependencies.get_retriever() is dependencies.get_retriever()
    assert dependencies.get_cache() is dependencies.get_cache()
