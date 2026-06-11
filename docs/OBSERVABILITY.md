# Observabilité

## Logs

Logs structurés JSON via `structlog` (`app/infrastructure/observability/logging.py`),
niveau configurable (`SHERPA_LOG_LEVEL`). Corrélation par `request-id` (middleware, Phase 1).

## Traces LLM (Phase 3)

**Langfuse** : trace de chaque appel (prompt, modèle, tokens, coût, latence), rattachée
à la requête. Permet le suivi coût/latence par fonctionnalité.

## Métriques (Phase 3)

**Prometheus** exposées sur `/metrics`, visualisées dans **Grafana** :

- latence des endpoints (histogramme), throughput, taux d'erreur ;
- tokens consommés, coût estimé ;
- taux de réponses ancrées, taux de refus hors-corpus.

## SLO / SLI

| SLI | SLO cible |
|---|---|
| Disponibilité `/ask` | 99.5 % |
| Latence p95 `/ask` | < 3 s |
| Taux de réponses ancrées | 100 % |

## Alerting

Alertes sur dépassement de budget tokens, hausse du taux d'erreur, latence p95 dégradée.
Procédures dans [RUNBOOK.md](RUNBOOK.md).
