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
- [x] Adapter `QdrantRetriever` (implémente `RetrieverPort`)
- [x] Adapter `VoyageEmbedding` (implémente `EmbeddingPort`)
- [x] Adapter `AnthropicLLM` (implémente `LLMPort`, routing multi-modèle)
- [x] Parsing PDF (PyMuPDF) / txt / md (`load_text`)
- [x] Retrieval hybride (dense + sparse) + fusion RRF
- [x] Switch de backend par config + wiring
- [x] Endpoint d'upload de fichier (multipart) branché sur `load_bytes`
- [ ] Test d'intégration Qdrant (testcontainers)
- [ ] Reranking cross-encoder
- [x] Persistance (Postgres + Alembic) — mémoire étudiant `study_events`
- [ ] Persistance métadonnées chunks (Postgres)

## Phase 2 — Agents
- [x] Agents `QuizGenerator`, `StudyPlanner`, `WeaknessDiagnoser` (services groundés + JSON validé)
- [x] Endpoints `/agents/quiz`, `/agents/study-plan`, `/agents/diagnose`
- [x] Câblage LangGraph (`AssistantOrchestrator` + endpoint `/assistant`)
- [ ] Routing d'intention par LLM (fallback règles)
- [x] Mémoire étudiant persistée (`study_events`) + `diagnose-from-history`
- [ ] Checkpointer LangGraph Postgres (état conversationnel)

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
