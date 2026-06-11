# Changelog

Tous les changements notables de ce projet sont documentés ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et ce projet respecte le [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]
### Added
- LLM-judge pour les évaluations : `evals/judge.py` (`LLMJudge` + `JudgeVerdict`, JSON validé)
  et runner `evals/judge_run.py` (`make judge`), actif sur le backend `anthropic`, ignoré sinon.
- Quota journalier par utilisateur : `DailyRequestQuota` + dépendance `enforce_quota`
  (off par défaut, `SHERPA_QUOTA_ENABLED` / `SHERPA_DAILY_REQUEST_QUOTA`) → `429`.

## [0.4.0] - 2026-06-11
### Added
- Persistance des métadonnées de chunks : `ChunkMetadataPort` + adapters `InMemoryChunkMetadata`
  (défaut) et `SqlChunkMetadata` (SQLAlchemy async), migration Alembic `chunk_meta` (0002).
  Enregistrement à l'ingestion.
- Suppression de cours (RGPD, droit à l'effacement) : `delete_course` sur `RetrieverPort`
  (in-memory, Qdrant, hybride) + endpoints `GET /courses/{id}/chunks` et `DELETE /courses/{id}`.
- Effacement étudiant (RGPD) : `delete_student` sur `StudyMemoryPort` (in-memory + SQL) +
  endpoint `DELETE /students/{id}` (supprime tout l'historique).
### Changed
- Orchestrateur LangGraph mémoïsé (`lru_cache`) : le graphe est compilé une seule fois
  par processus au lieu d'être reconstruit à chaque requête.

## [0.3.0] - 2026-06-11
### Added
- Cache LLM : `CachePort` + adapters `InMemoryCache` (défaut, TTL) et `RedisCache` (async).
  Décorateur `CachingLLM` qui court-circuite les complétions identiques (clé = hash
  système+prompt+modèle+max_tokens). Activé sur le backend `anthropic` ; réglable via
  `SHERPA_LLM_CACHE_ENABLED`, `SHERPA_LLM_CACHE_TTL_SECONDS`, `SHERPA_CACHE_BACKEND`.
- Cache des embeddings : `CachingEmbedding` (cache par texte, ne calcule que les manquants
  en un seul batch). Activé sur le backend `hybrid` ; réglable via
  `SHERPA_EMBEDDING_CACHE_ENABLED`, `SHERPA_EMBEDDING_CACHE_TTL_SECONDS`.
- Sécurité API : authentification par clé (`X-API-Key`) et rate-limiting fenêtre fixe
  (`FixedWindowRateLimiter`), désactivés par défaut, sur les routes applicatives
  (`/`, `/healthz`, `/metrics` restent publiques). Config `SHERPA_AUTH_ENABLED`,
  `SHERPA_API_KEYS`, `SHERPA_RATE_LIMIT_*`. → `401` / `429`.

## [0.2.0] - 2026-06-11
### Added
- Phase 1 : adapters de production derrière les ports existants.
  - `VoyageEmbedding` (EmbeddingPort) et `AnthropicLLM` / Claude (LLMPort), imports lazy, clients injectables.
  - `QdrantRetriever` (RetrieverPort) + helpers de mapping purs testés.
  - `reciprocal_rank_fusion` (RRF) et `HybridRetriever` (dense + sparse).
  - Chargement de documents `.pdf` / `.txt` / `.md` (`load_text`, PyMuPDF lazy).
- Sélection de backend par configuration (`SHERPA_RETRIEVAL_BACKEND`, `SHERPA_LLM_BACKEND`)
  avec wiring dans la composition root ; défaut `memory`/`echo` (hors-ligne).
- Endpoint `POST /ingest/file` (multipart) : upload `.pdf`/`.txt`/`.md` → ingestion
  (`load_bytes`, PDF en flux), `415` si type non supporté.
- Phase 2 (agents) : `QuizGenerator`, `StudyPlanner`, `WeaknessDiagnoser` (couche application,
  groundés via retrieval, sorties JSON validées Pydantic). Endpoints `POST /agents/quiz`,
  `/agents/study-plan`, `/agents/diagnose`. Sortie LLM invalide → `502` (`AgentOutputError`).
- Orchestration LangGraph : `AssistantOrchestrator` (graphe routant `tutor`/`quiz`/`plan`
  selon `classify_intent`) exposé via `POST /assistant`. Extra `agents` (`langgraph`).
- Mémoire étudiant : `StudyMemoryPort` + adapters `InMemoryStudyMemory` (défaut) et
  `SqlStudyMemory` (SQLAlchemy async). Endpoints `POST /memory/answers`, `GET /memory/history`,
  `POST /agents/diagnose-from-history`. Migrations Alembic (`study_events`). Backend via
  `SHERPA_MEMORY_BACKEND` (`memory`/`sql`).
- Observabilité (Phase 3) : métriques Prometheus sur `GET /metrics` (compteur + histogramme
  de latence, label `path` = template de route), middleware `X-Request-ID` corrélé aux logs
  structlog, log d'accès par requête.
- UI de démo : page unique (HTML/CSS/JS vanilla, sans build) servie sur `GET /` — ingestion
  texte/fichier + chat branché sur `/assistant` (rendu answer/quiz/plan + citations).
- Résilience (Phase 4) : `ResilientLLM` enveloppe le LLM avec timeout, retries + backoff
  exponentiel (`retry_async`), circuit breaker (`CircuitBreaker`) et garde-fou de budget
  (`DailyTokenBudget` → 429). Activé sur le backend `anthropic`, réglable par config.

## [0.1.0] - 2026-06-11
### Added
- Fondations (Phase 0) : clean architecture en couches (domain / application / infrastructure / presentation).
- Configuration `pydantic-settings` et logging structuré (structlog).
- API FastAPI : `/healthz`, `/ingest`, `/ask` avec citations et refus gracieux hors-corpus.
- Adapters hors-ligne par défaut : `InMemoryRetriever` (TF-IDF) et `EchoLLM`.
- Pipeline d'ingestion idempotent (chunking + hash de contenu).
- Suite de tests (unitaires + intégration) et evals golden set.
- Outillage qualité : ruff, mypy --strict, pytest, pre-commit, bandit, gitleaks.
- Docker multi-stage, docker-compose (qdrant / postgres / redis), CI GitHub Actions.
- Documentation complète (PROJECT, ROADMAP, docs/*, ADR).

[Unreleased]: https://github.com/SeydinaBANE/sherpa/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/SeydinaBANE/sherpa/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/SeydinaBANE/sherpa/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/SeydinaBANE/sherpa/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/SeydinaBANE/sherpa/releases/tag/v0.1.0
