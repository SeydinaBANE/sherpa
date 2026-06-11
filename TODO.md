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
- [x] Persistance métadonnées chunks (`chunk_meta`) + suppression de cours (RGPD)

## Phase 2 — Agents
- [x] Agents `QuizGenerator`, `StudyPlanner`, `WeaknessDiagnoser` (services groundés + JSON validé)
- [x] Endpoints `/agents/quiz`, `/agents/study-plan`, `/agents/diagnose`
- [x] Câblage LangGraph (`AssistantOrchestrator` + endpoint `/assistant`)
- [ ] Routing d'intention par LLM (fallback règles)
- [x] Mémoire étudiant persistée (`study_events`) + `diagnose-from-history`
- [ ] Checkpointer LangGraph Postgres (état conversationnel)

## Phase 3 — Evals + Observabilité
- [x] Métriques Prometheus (`/metrics`) + middleware request-id + access logging
- [ ] Traces LLM Langfuse (coûts/latence par appel)
- [ ] Dashboards Grafana + SLO/SLI + alerting
- [ ] Intégration RAGAS + LLM-judge (Claude Opus)
- [ ] Dataset d'eval versionné + seuils bloquants en CI

## Phase 4 — Optimisation & résilience
- [x] Retries/backoff, circuit breaker, timeout (`ResilientLLM`)
- [x] Budget de tokens quotidien (`DailyTokenBudget` → 429)
- [x] Cache LLM (`CachePort` + `CachingLLM`, in-memory/Redis)
- [x] Cache des embeddings (`CachingEmbedding`, batch des manquants)
- [x] Quotas par utilisateur (`DailyRequestQuota` → 429)

## Démo
- [x] UI de démo (page unique servie sur `/` : ingestion + chat tutor/quiz/plan)

## Phase 5 — Déploiement
- [x] Pipeline déploiement Cloud Run (canary `--no-traffic`) + smoke test + promotion
- [x] Manifeste Cloud Run (`infra/cloudrun.yaml`)
- [ ] Branchement réel GCP (Workload Identity, Secret Manager)
- [x] Scan d'image (Trivy) en CI
- [ ] pip-audit en CI
- [x] Conformité RGPD (effacement cours & étudiant) — rétention/runbook à compléter
