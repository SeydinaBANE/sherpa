# ADR 0003 — Base vectorielle : Qdrant

- Statut : accepté
- Date : 2026-06-11

## Contexte

Le RAG a besoin d'une recherche sémantique avec filtrage par métadonnées (par cours,
par source), facile à exécuter en local et à opérer en production.

## Décision

Adopter **Qdrant** comme base vectorielle, derrière `RetrieverPort`.

## Alternatives

- **pgvector** : pratique (réutilise Postgres) mais moins performant à grande échelle et
  fonctions de filtrage/hybridation moins riches.
- **Pinecone / managé propriétaire** : opérationnellement simple mais lock-in et coût.

## Conséquences

- Recherche hybride et filtrage métadonnées natifs.
- Service supplémentaire à opérer (compose en dev, managé en prod).
- L'abstraction `RetrieverPort` permet de revenir à pgvector si besoin.
