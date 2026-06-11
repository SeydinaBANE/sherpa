# Sherpa — Tuteur IA pour la préparation d'examens

> Transforme les supports de cours d'un étudiant en un assistant de révision **fiable, ancré (citations) et adaptatif**.

Sherpa est un produit GenAI **production-grade** : RAG ancré, agents spécialisés, evals, monitoring, optimisation coût/latence. Il sert aussi de démonstrateur d'architecture IA moderne (clean architecture, typage strict, tests, CI/CD).

## Pourquoi

En éducation, une réponse non sourcée est inutilisable. Sherpa ne répond **que** depuis le corpus du cours et **cite systématiquement** ses sources — sinon il refuse de répondre.

## Fonctionnalités

- **Ingestion** : supports de cours → chunks indexés (idempotent).
- **RAG ancré** : retrieval + réponse citée, refus gracieux hors-corpus.
- **Agents** (roadmap) : quiz, plan de révision, diagnostic des points faibles.
- **Production** : monitoring (Langfuse + Prometheus), evals (RAGAS), Docker, CI/CD.

## Stack

Python 3.11 · FastAPI · LangGraph · Qdrant · Postgres · Redis · Claude (routing multi-modèle) · Voyage AI · Langfuse · Prometheus/Grafana · Docker · GitHub Actions.

> Le code fonctionne **hors-ligne par défaut** grâce à des adapters in-memory (`InMemoryRetriever`, `EchoLLM`). Les adapters de production (Qdrant + Claude + Voyage) s'activent via les extras `[rag]`, `[data]`, `[observability]`.

## Architecture

Clean architecture en couches (`domain` → `application` → `infrastructure` → `presentation`).
Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Démarrage rapide

```bash
make install        # venv + dépendances dev
cp .env.example .env
make test           # lance la suite de tests
make dev            # API + UI de démo sur http://localhost:8000
```

- **UI de démo** : http://localhost:8000/ (ingestion + chat tutor/quiz/plan)
- **Docs OpenAPI** : http://localhost:8000/docs
- **Métriques** : http://localhost:8000/metrics

Exemple end-to-end :

```bash
curl -s -X POST localhost:8000/ingest \
  -H 'content-type: application/json' \
  -d '{"course_id":"bio","source":"cours.pdf","text":"La photosynthèse transforme la lumière en énergie."}'

curl -s -X POST localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"course_id":"bio","question":"Que fait la photosynthèse ?"}'
```

## Qualité

```bash
make lint        # ruff
make typecheck   # mypy --strict
make test        # pytest + couverture
make precommit   # tous les hooks
```

## Documentation

| Doc | Contenu |
|---|---|
| [PROJECT.md](PROJECT.md) | Vision, personae, périmètre, métriques |
| [ROADMAP.md](ROADMAP.md) | Jalons |
| [TODO.md](TODO.md) | Backlog par phases |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Workflow git & conventions |
| [docs/](docs/) | Architecture, RAG, evals, sécurité, RGPD, runbook… |

## Licence

MIT — voir [LICENSE](LICENSE).
