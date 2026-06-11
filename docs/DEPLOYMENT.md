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

## Pipeline (`.github/workflows/deploy.yml`)

Déclencheurs : tag `v*` ou `workflow_dispatch`. **Opt-in** : le job ne s'exécute que si la
variable de dépôt `DEPLOY_ENABLED == 'true'` (sinon ignoré → la CI ne casse jamais sans secrets).

```
tag v* → auth GCP (Workload Identity) → build & push image (Artifact Registry)
       → deploy Cloud Run en --no-traffic (révision canary)
       → smoke test sur l'URL de la révision
       → promotion du trafic vers la dernière révision (--to-latest)
```

### Configuration requise (à créer côté GitHub/GCP)

- Variables de dépôt : `DEPLOY_ENABLED=true`, `GCP_PROJECT`, `GCP_REGION`.
- Secrets : `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT` (Workload Identity Federation).
- Secrets applicatifs (clés API, URLs DB/Redis/Qdrant) dans **Secret Manager**, injectés
  dans Cloud Run (cf. `infra/cloudrun.yaml`).

## Smoke tests

`scripts/smoke_test.py` (aussi `make smoke BASE_URL=...`) : `GET /healthz` == 200, puis
`/ingest` et `/ask` sur un cours de référence → réponse **ancrée**. Exécuté automatiquement
sur la révision canary avant promotion du trafic.

## Rollback

Re-router le trafic Cloud Run vers la révision précédente (les révisions sont conservées).

## Migrations

Postgres via Alembic (`make migrate`, Phase 1) — appliquées avant le basculement de trafic.
