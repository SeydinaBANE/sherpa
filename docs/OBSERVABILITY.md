# Observabilité

## Logs ✅

Logs structurés JSON via `structlog` (`app/infrastructure/observability/logging.py`),
niveau configurable (`SHERPA_LOG_LEVEL`). **Corrélation par `request-id`** : le middleware
(`app/presentation/middleware.py`) génère ou propage l'en-tête `X-Request-ID`, le lie au
contexte structlog (présent dans chaque log de la requête) et le renvoie dans la réponse.
Chaque requête émet un log `request` (méthode, route, statut, durée ms).

## Métriques ✅

**Prometheus** exposées sur **`GET /metrics`** (`app/infrastructure/observability/metrics.py`) :

- `sherpa_http_requests_total{method,path,status}` — compteur de requêtes ;
- `sherpa_http_request_duration_seconds{method,path}` — histogramme de latence.

Le label `path` utilise le **template de route** (pas l'URL brute) pour borner la cardinalité.
À visualiser dans **Grafana**.

## Traces LLM (à venir)

**Langfuse** : trace de chaque appel (prompt, modèle, tokens, coût, latence) rattachée à la
requête — clés déjà prévues dans la config (`SHERPA_LANGFUSE_*`).

## SLO / SLI

| SLI | SLO cible |
|---|---|
| Disponibilité `/ask` | 99.5 % |
| Latence p95 `/ask` | < 3 s |
| Taux de réponses ancrées | 100 % |

## Alerting

Alertes sur dépassement de budget tokens, hausse du taux d'erreur, latence p95 dégradée.
Procédures dans [RUNBOOK.md](RUNBOOK.md).
