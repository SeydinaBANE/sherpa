# Conception RAG

## Objectif

Répondre **uniquement** depuis le corpus du cours, avec citations vérifiables.
Aucune réponse hors-source : en l'absence de contexte pertinent, refus gracieux (HTTP 422).

## Pipeline

1. **Ingestion** (`app/application/ingestion/chunker.py`)
   - Normalisation, découpage par paragraphes regroupés jusqu'à `max_chars`.
   - `Chunk.create` calcule un `chunk_id` = SHA-256(course:source:ordinal:text) → **idempotence**.
2. **Indexation** (`RetrieverPort.index`)
   - In-memory (TF-IDF) par défaut ; Qdrant + embeddings Voyage en production.
   - Ré-indexer un contenu identique est un no-op.
3. **Retrieval** (`RetrieverPort.retrieve`)
   - In-memory : score TF-IDF cosine simplifié, top-k.
   - Production (cible) : hybride dense (Qdrant) + sparse (BM25), fusion **RRF**, reranking.
4. **Génération** (`app/application/rag/service.py` + `prompts.py`)
   - System prompt impose la citation `[source:ordinal]` et le refus hors-contexte.
   - Réponse + `Citation` extraites des chunks récupérés.

## Garde-fous anti-hallucination

- Pas de chunk pertinent → `NoRelevantContextError` (jamais de réponse inventée).
- `Answer.is_grounded` = au moins une citation.
- Eval `grounding` à 1.0 attendu (voir [EVALS.md](EVALS.md)).

## Paramètres clés

| Paramètre | Défaut | Où |
|---|---|---|
| `max_chars` (chunk) | 1200 | `chunker.chunk_document` |
| `top_k` | 4 | `RagService` |
| `max_tokens` | `SHERPA_MAX_TOKENS_PER_REQUEST` | config |
| modèle | `SHERPA_LLM_MODEL_STANDARD` | config |

## Évolutions prévues (Phase 1)

Reranking cross-encoder, déduplication de chunks, fenêtre de contexte adaptative,
citations au niveau de la phrase.
