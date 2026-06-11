# Runbook

Procédures d'exploitation et de remédiation d'incidents.

## Healthcheck

- `GET /healthz` doit renvoyer `{"status":"ok"}`.
- Docker : `HEALTHCHECK` intégré à l'image (voir `docker/Dockerfile`).

## Incidents fréquents

### L'API renvoie beaucoup de 422 sur `/ask`
- **Cause probable** : corpus non indexé pour le `course_id`.
- **Action** : vérifier l'ingestion (`/ingest`), recharger les documents du cours.

### Latence p95 dégradée
- Vérifier la santé de Qdrant et du fournisseur LLM.
- Vérifier le cache Redis (taux de hit).
- Basculer le routing vers un modèle plus rapide si nécessaire.

### Budget de tokens dépassé (429)
- Inspecter les coûts par fonctionnalité dans Langfuse.
- Ajuster `SHERPA_DAILY_TOKEN_BUDGET` / quotas, identifier l'usage anormal.

### Dépendance externe indisponible (LLM/Qdrant)
- Les appels ont timeouts + retries/backoff + circuit breaker (Phase 4).
- Dégradation gracieuse : fallback modèle, message d'indisponibilité.

## Rollback

Voir [DEPLOYMENT.md](DEPLOYMENT.md) — Cloud Run conserve les révisions, rollback en
re-routant le trafic vers la révision précédente.

## Astreinte

- Canaux d'alerte : à définir (PagerDuty/Slack).
- Escalade : on-call → mainteneurs → lead IA.
