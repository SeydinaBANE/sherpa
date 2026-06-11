# Déploiement

## Environnements

| Env | Branche | Usage |
|---|---|---|
| local | `develop` | dev (docker-compose) |
| staging | `develop` | pré-prod, tests d'intégration |
| production | `main` | clients |

## Build

Image Docker multi-stage (`docker/Dockerfile`), exécutée en utilisateur non-root,
healthcheck intégré. Construite en CI (job `docker`).

## Cible : GCP Cloud Run

- Service stateless `sherpa-api` (image du registre).
- Qdrant et Postgres **managés** (ou Cloud SQL + Qdrant Cloud).
- Secrets via **Secret Manager** (jamais en clair).
- Variables d'env injectées par environnement.

## Pipeline (cible Phase 5)

```
push main → CI (lint, types, tests, evals, scans, build)
          → push image registre
          → deploy Cloud Run (révision canary, ex. 10 % trafic)
          → smoke tests sur l'URL
          → promotion 100 % ou rollback
```

## Smoke tests

- `GET /healthz` == 200.
- `/ingest` puis `/ask` sur un cours de référence → réponse ancrée.

## Rollback

Re-router le trafic Cloud Run vers la révision précédente (les révisions sont conservées).

## Migrations

Postgres via Alembic (`make migrate`, Phase 1) — appliquées avant le basculement de trafic.
