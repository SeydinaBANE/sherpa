# TODO — Sherpa

Backlog priorisé par phases (voir [ROADMAP.md](ROADMAP.md)).

## Phase 0 — Fondations ✅
- [x] Scaffolding clean architecture (domain/application/infrastructure/presentation)
- [x] Config `pydantic-settings` + logging structuré
- [x] Endpoints `/healthz`, `/ingest`, `/ask` (adapters in-memory)
- [x] Tests unitaires + intégration (12)
- [x] ruff, mypy --strict, pytest, coverage
- [x] pre-commit (ruff, mypy, bandit, gitleaks, conventional commits)
- [x] Dockerfile multi-stage + docker-compose (qdrant/postgres/redis)
- [x] CI GitHub Actions + evals golden set
- [x] Documentation complète

## Phase 1 — Ingestion + RAG production
- [ ] Adapter `QdrantRetriever` (implémente `RetrieverPort`)
- [ ] Adapter `VoyageEmbedding` (implémente `EmbeddingPort`)
- [ ] Adapter `AnthropicLLM` (implémente `LLMPort`, routing multi-modèle)
- [ ] Parsing PDF (PyMuPDF) + chunking sémantique
- [ ] Retrieval hybride (dense + BM25) + RRF + reranking
- [ ] Persistance métadonnées chunks (Postgres + Alembic)

## Phase 2 — Agents
- [ ] Graphe LangGraph + état + checkpointer Postgres
- [ ] Agents `quiz_generator`, `study_planner`, `weakness_diagnoser`
- [ ] Mémoire étudiant (suivi des lacunes)

## Phase 3 — Evals + Observabilité
- [ ] Intégration RAGAS + LLM-judge (Claude Opus)
- [ ] Dataset d'eval versionné + seuils bloquants en CI
- [ ] Langfuse + Prometheus/Grafana + SLO/SLI + alerting

## Phase 4 — Optimisation & résilience
- [ ] Cache Redis + batching embeddings
- [ ] Retries/backoff, circuit breaker (tenacity)
- [ ] Quotas par utilisateur + budgets coûts

## Phase 5 — Déploiement
- [ ] Pipeline déploiement Cloud Run + canary + smoke tests
- [ ] Scans sécurité (pip-audit, Trivy) + secrets manager
- [ ] Conformité RGPD (rétention, effacement) + runbook
