# Performance

Méthodologie de mesure et cibles. Principe : **optimiser ce qui est mesuré** — pas
d'optimisation à l'aveugle. Voir aussi [COST.md](COST.md) et [OBSERVABILITY.md](OBSERVABILITY.md).

## Indicateurs suivis

| Indicateur | Source | Cible (v1) |
|---|---|---|
| Latence p95 `/ask` | histogramme Prometheus `sherpa_http_request_duration_seconds` | < 3 s |
| Latence p95 `/assistant` | idem (label `path`) | < 4 s |
| Temps de retrieval | trace applicative (à instrumenter) | < 300 ms |
| Coût moyen / requête | Langfuse (à câbler) | suivi & budgété |
| Débit (req/s) | `sherpa_http_requests_total` (dérivée) | dépend de l'instance |

## Décomposition d'une requête `/ask`

```
embed(query) → retrieval (Qdrant + BM25 + RRF) → assemblage contexte → appel LLM
```

Le poste dominant en production est **l'appel LLM** (réseau + génération). Les leviers :

1. **Routing multi-modèle** — Haiku pour le simple, Sonnet par défaut, Opus si nécessaire.
2. **Cache Redis** (à venir) — réponses et embeddings réutilisés.
3. **Batching** des embeddings à l'ingestion.
4. **Contexte borné** — `top_k` limité, chunks dédupliqués, `max_tokens` plafonné.

## Mesures actuelles

- **Chemin hors-ligne** (backends `memory`/`echo`) : suite de tests complète < 1 s ;
  `/ask` répond en ~1 ms hors LLM réel (voir smoke test). Utile pour le débit du retrieval
  et la CI, **pas représentatif** de la latence LLM de production.
- **Chemin production** (Claude + Qdrant) : *à mesurer* sous charge réelle.

## Protocole de benchmark (à exécuter)

1. Jeu de requêtes représentatif + corpus de référence indexé.
2. Charge progressive (ex. `k6`/`locust`) sur `/ask` et `/assistant`.
3. Relever p50/p95/p99 (Prometheus) et le coût/latence par appel (Langfuse).
4. Comparer **avant/après** chaque optimisation (cache, routing) pour prouver le gain.

> Statut : instrumentation Prometheus en place ; benchmarks de charge et traces de coût
> Langfuse restent à câbler — cf. [DETTE-TECHNIQUE](../DETTE-TECHNIQUE.md).
