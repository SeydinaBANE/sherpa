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
- ✅ Câblage LangGraph (`AssistantOrchestrator`, routing d'intention, endpoint `/assistant`).
- ✅ Mémoire étudiant persistée (`StudyMemoryPort`, SQLAlchemy + Alembic, `diagnose-from-history`).
- ⬜ Checkpointer LangGraph Postgres (état conversationnel).

## Phase 3 — Evals + Observabilité 🔶
- ✅ Métriques Prometheus (`/metrics`) + middleware request-id + access logging structuré.
- ⬜ Langfuse (traces LLM, coûts).
- ⬜ RAGAS + LLM-judge sur golden dataset versionné, seuils bloquants en CI.
- ⬜ Dashboards Grafana + SLO/SLI + alerting.

## Phase 4 — Optimisation & résilience ✅
- ✅ Retries/backoff, circuit breaker, timeout (`ResilientLLM`) + budget tokens (`DailyTokenBudget`).
- ✅ Cache LLM (`CachingLLM`) + cache des embeddings (`CachingEmbedding`), in-memory/Redis.
- ✅ Quotas par utilisateur (`DailyRequestQuota`).

## Phase 5 — Déploiement 🔶
- ✅ Pipeline de déploiement (`deploy.yml`) : Cloud Run, canary `--no-traffic`, smoke test, promotion.
- ✅ Smoke test (`scripts/smoke_test.py`) + manifeste `infra/cloudrun.yaml`.
- ✅ Scan d'image Trivy en CI (HIGH/CRITICAL).
- ⬜ Branchement réel GCP (Workload Identity, Secret Manager).
- ⬜ Canary monitoring & runbook on-call.
