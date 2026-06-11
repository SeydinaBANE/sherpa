# Changelog

Tous les changements notables de ce projet sont documentés ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et ce projet respecte le [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]
### Added
- Phase 1 (en cours) : adapters de production derrière les ports existants.
  - `VoyageEmbedding` (EmbeddingPort) et `AnthropicLLM` / Claude (LLMPort), imports lazy, clients injectables.
  - `QdrantRetriever` (RetrieverPort) + helpers de mapping purs testés.
  - `reciprocal_rank_fusion` (RRF) et `HybridRetriever` (dense + sparse).
  - Chargement de documents `.pdf` / `.txt` / `.md` (`load_text`, PyMuPDF lazy).
- Sélection de backend par configuration (`SHERPA_RETRIEVAL_BACKEND`, `SHERPA_LLM_BACKEND`)
  avec wiring dans la composition root ; défaut `memory`/`echo` (hors-ligne).

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

[Unreleased]: https://github.com/your-org/sherpa/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/sherpa/releases/tag/v0.1.0
