# ROADMAP — Sherpa

> Statut : ✅ fait · 🔶 en cours · ⬜ à venir

## Phase 0 — Fondations ✅
- Clean architecture en couches, config, logging structuré.
- API FastAPI (`/healthz`, `/ingest`, `/ask`) avec adapters in-memory hors-ligne.
- Qualité : ruff, mypy --strict, pytest, pre-commit, CI, Docker, evals golden set.

## Phase 1 — Ingestion + RAG production 🔶
- Adapter Qdrant (vectoriel) + embeddings Voyage AI.
- Parsing PDF/slides (PyMuPDF), chunking sémantique avancé.
- Retrieval hybride (dense + BM25), fusion RRF, reranking.
- Adapter Claude (routing multi-modèle) en remplacement de `EchoLLM`.

## Phase 2 — Agents 🔶
- ✅ Agents `QuizGenerator`, `StudyPlanner`, `WeaknessDiagnoser` (services groundés, JSON validé) + endpoints.
- ⬜ Câblage LangGraph (graphe, routing, état partagé).
- ⬜ Mémoire étudiant persistée (checkpointer Postgres).

## Phase 3 — Evals + Observabilité ⬜
- RAGAS + LLM-judge sur golden dataset versionné, seuils bloquants en CI.
- Langfuse (traces, coûts) + Prometheus/Grafana (latence, throughput), SLO/SLI.

## Phase 4 — Optimisation & résilience ⬜
- Cache Redis (réponses/embeddings), batching embeddings.
- Retries/backoff, circuit breaker, quotas & budgets coûts.

## Phase 5 — Déploiement ⬜
- CI/CD complet, scans sécurité (deps, image, secrets), conformité RGPD.
- Déploiement GCP Cloud Run, canary + smoke tests, runbook on-call.
