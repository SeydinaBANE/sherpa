# ADR 0002 — Clean architecture et ports/adapters

- Statut : accepté
- Date : 2026-06-11

## Contexte

Le produit doit passer de POC à production sans réécriture. Les briques externes
(LLM, base vectorielle, embeddings) évoluent vite et doivent être interchangeables.
Les tests doivent tourner sans dépendances réseau.

## Décision

Architecture en couches avec inversion de dépendance. Le domaine expose des **ports**
(`typing.Protocol`) ; l'infrastructure fournit des **adapters**. Adapters in-memory par
défaut (`InMemoryRetriever`, `EchoLLM`), adapters de production via extras (`rag`, `data`).

## Alternatives

- Couplage direct à LangChain/Qdrant dans les use-cases : rapide mais rigide, tests lents.
- Framework lourd (hexagonal complet avec DI container) : surdimensionné pour la v1.

## Conséquences

- Tests rapides et déterministes (pas de réseau).
- Remplacement d'un fournisseur sans toucher au domaine.
- Un peu plus de code de wiring (composition root).
