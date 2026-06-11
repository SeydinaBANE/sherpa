# Stratégie de tests

## Philosophie

Tout est **testable hors-ligne** : les services externes (LLM, base vectorielle, DB) sont
derrière des ports, avec des adapters in-memory/faux par défaut. Aucun test n'appelle le
réseau → suite rapide et déterministe.

## Pyramide

| Niveau | Cible | Exemples |
|---|---|---|
| Unitaire | logique pure | `test_chunker`, `test_fusion`, `test_resilience`, `test_qdrant_mapping` |
| Composant | services + adapters | `test_rag_service`, `test_agents`, `test_retriever`, `test_memory` |
| Intégration | API end-to-end | `test_api*` (FastAPI via `httpx.AsyncClient`) |
| Données | SQL réel | `test_memory` sur SQLite (`aiosqlite`) |

## Conventions

- Nommage : `test_<fonction>_<cas>` ; au moins un cas nominal + un cas d'erreur.
- `asyncio_mode = auto` (pas de décorateur nécessaire sur les tests async).
- Injection de dépendances pour les agents/LLM via **faux clients** ; surcharge des routes
  via `app.dependency_overrides` pour les tests API.
- Les singletons (`get_retriever`, `get_llm`, `get_study_memory`) sont remis à zéro entre
  tests (`conftest.py`).

## Lancer

```bash
make test        # suite complète
make cov         # avec couverture (seuil informatif: 70 %)
make evals       # évaluations RAG (golden set)
```

## En CI

`.github/workflows/ci.yml` exécute : `ruff` (lint+format), `mypy --strict`, `bandit`,
`pytest --cov`, puis `python -m evals.run` (seuils bloquants), enfin le build Docker.

## À venir

- Tests d'intégration Qdrant (`testcontainers`), cf. [DETTE-TECHNIQUE](../DETTE-TECHNIQUE.md).
- RAGAS + LLM-judge, cf. [EVALS](EVALS.md).
