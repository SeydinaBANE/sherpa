# Coûts & optimisation

## Leviers

1. **Routing multi-modèle** (voir [adr/0004](adr/0004-llm-routing-claude.md))
   - Haiku pour les tâches simples, Sonnet par défaut, Opus seulement si nécessaire.
2. **Cache Redis** (Phase 4) : réponses et embeddings réutilisés.
3. **Batching** des embeddings à l'ingestion.
4. **Contrôle de contexte** : top-k borné, chunks dédupliqués, `max_tokens` plafonné.

## Garde-fous ✅

- `SHERPA_MAX_TOKENS_PER_REQUEST` : plafond par requête.
- `SHERPA_DAILY_TOKEN_BUDGET` : budget quotidien appliqué par `DailyTokenBudget`
  (`app/infrastructure/resilience/budget.py`) ; dépassement → `BudgetExceededError` (429).
- **Résilience** (`ResilientLLM`) : timeout, retries + backoff exponentiel, circuit breaker.
- Quotas par utilisateur : à venir.

## Suivi

- Coût par requête et par fonctionnalité via Langfuse (Phase 3).
- Alerte sur dépassement de budget (voir [OBSERVABILITY.md](OBSERVABILITY.md)).

## Méthode

Mesurer avant/après chaque optimisation (latence p95 et coût moyen / requête) pour
prouver le gain — pas d'optimisation à l'aveugle.
