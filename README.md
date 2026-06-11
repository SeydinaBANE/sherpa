# Sherpa — Tuteur IA pour la préparation d'examens

[![CI](https://github.com/SeydinaBANE/sherpa/actions/workflows/ci.yml/badge.svg)](https://github.com/SeydinaBANE/sherpa/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/SeydinaBANE/sherpa?sort=semver)](https://github.com/SeydinaBANE/sherpa/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Typed: mypy strict](https://img.shields.io/badge/mypy-strict-2A6DB2)](https://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/tests-60%20passing-4ade80)](tests/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Transforme les supports de cours d'un étudiant en un assistant de révision **fiable, ancré (citations) et adaptatif**.

Sherpa est un produit GenAI **production-grade** : RAG ancré, agents spécialisés, orchestration LLM, observabilité et résilience. Il sert aussi de démonstrateur d'architecture IA moderne (clean architecture, typage strict, tests, CI/CD).

## Pourquoi

En éducation, une réponse non sourcée est inutilisable. Sherpa ne répond **que** depuis le corpus du cours et **cite systématiquement** ses sources — sinon il refuse de répondre.

## Fonctionnalités

- **Ingestion** : supports de cours (texte + fichiers `.pdf`/`.txt`/`.md`) → chunks indexés (idempotent).
- **RAG ancré** : retrieval hybride (dense + BM25) + fusion RRF, réponse citée, refus gracieux hors-corpus.
- **Agents** : génération de quiz, plan de révision, diagnostic des points faibles (sorties JSON validées).
- **Orchestration** : graphe **LangGraph** routant un message libre vers le bon agent (`/assistant`).
- **Mémoire étudiant** : historique persisté (SQLAlchemy + Alembic) → diagnostic adaptatif.
- **Observabilité** : métriques Prometheus (`/metrics`), `X-Request-ID` corrélé aux logs structurés.
- **Résilience & coûts** : timeout, retries + backoff, circuit breaker, budget de tokens.

> Le code fonctionne **hors-ligne par défaut** (adapters `InMemoryRetriever`, `EchoLLM`,
> mémoire en RAM). Les adapters de production (Qdrant + Claude + Voyage + Postgres)
> s'activent par configuration (`SHERPA_*_BACKEND`) et via les extras `[rag]`, `[data]`, `[agents]`.

## Stack

Python 3.11 · FastAPI · LangGraph · Qdrant · Postgres · Redis · Claude (routing multi-modèle) · Voyage AI · Prometheus · Docker · GitHub Actions.

## Architecture

Clean architecture en couches (`domain` → `application` → `infrastructure` → `presentation`),
inversion de dépendance par ports/adapters. Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Démarrage rapide

```bash
make install        # venv + dépendances dev + hooks pre-commit
cp .env.example .env
make test           # lance la suite de tests
make dev            # API + UI de démo sur http://localhost:8000
```

- **UI de démo** : http://localhost:8000/ (ingestion + chat tutor/quiz/plan)
- **Docs OpenAPI** : http://localhost:8000/docs
- **Métriques** : http://localhost:8000/metrics

## API (aperçu)

| Endpoint | Rôle |
|---|---|
| `POST /ingest` · `POST /ingest/file` | Indexer un cours (texte ou fichier) |
| `POST /ask` | Q&A RAG ancré avec citations |
| `POST /assistant` | Orchestrateur LangGraph (tutor / quiz / plan) |
| `POST /agents/quiz` · `/study-plan` · `/diagnose` | Agents dédiés |
| `POST /memory/answers` · `GET /memory/history` | Mémoire étudiant |
| `POST /agents/diagnose-from-history` | Diagnostic à partir de l'historique |
| `GET /healthz` · `GET /metrics` | Santé & métriques |

Exemple end-to-end :

```bash
curl -s -X POST localhost:8000/ingest \
  -H 'content-type: application/json' \
  -d '{"course_id":"bio","source":"cours.pdf","text":"La photosynthèse transforme la lumière en énergie."}'

curl -s -X POST localhost:8000/assistant \
  -H 'content-type: application/json' \
  -d '{"course_id":"bio","message":"Donne-moi un quiz sur la photosynthèse"}'
```

## Qualité

```bash
make lint        # ruff
make typecheck   # mypy --strict
make test        # pytest + couverture
make evals       # évaluations RAG (golden set)
make precommit   # tous les hooks (ruff, mypy, bandit, gitleaks, conventional commits)
```

## Documentation

| Doc | Contenu |
|---|---|
| [PROJECT.md](PROJECT.md) | Vision, personae, périmètre, métriques |
| [ROADMAP.md](ROADMAP.md) · [TODO.md](TODO.md) | Jalons & backlog par phases |
| [DETTE-TECHNIQUE.md](DETTE-TECHNIQUE.md) | Registre de dette technique |
| [CONTRIBUTING.md](CONTRIBUTING.md) · [SUPPORT.md](SUPPORT.md) | Workflow git & obtenir de l'aide |
| [docs/](docs/README.md) | Architecture, ADR, configuration, tests, release, evals, RGPD, runbook… |

## Licence

MIT — voir [LICENSE](LICENSE).
