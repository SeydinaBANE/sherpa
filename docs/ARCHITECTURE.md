# Architecture

## Vue d'ensemble

Sherpa applique une **clean architecture** : les dépendances pointent vers l'intérieur.
Le domaine ne connaît ni le web, ni la base, ni le LLM.

```
┌─────────────────────────────────────────────────────────┐
│  presentation  — FastAPI, schémas Pydantic, handlers      │
│                  d'exceptions, dépendances (composition)   │
├─────────────────────────────────────────────────────────┤
│  application   — use-cases : ingestion (chunker),          │
│                  rag (service + prompts)                    │
├─────────────────────────────────────────────────────────┤
│  domain        — entités (Chunk, Answer, Citation),        │
│                  ports (Protocol), exceptions métier        │
├─────────────────────────────────────────────────────────┤
│  infrastructure— adapters : retrieval (in-memory/Qdrant),  │
│                  llm (echo/Claude), observability (logs)    │
└─────────────────────────────────────────────────────────┘
```

## Inversion de dépendance

Le domaine définit des **ports** (`RetrieverPort`, `LLMPort`, `EmbeddingPort` — `app/domain/ports.py`)
sous forme de `typing.Protocol`. L'application dépend de ces ports, jamais des adapters.

- Hors-ligne (défaut) : `InMemoryRetriever`, `EchoLLM`.
- Production : `QdrantRetriever` + `VoyageEmbedding` + `AnthropicLLM` (extras `rag`).

Conséquence : on remplace l'implémentation sans toucher au domaine ni aux use-cases.
La composition se fait dans `app/presentation/dependencies.py`.

## Flux RAG (`/ask`)

```
question
  → retriever.retrieve(course_id, query, top_k)   (lexical / vectoriel hybride)
  → si vide : NoRelevantContextError (422)
  → build_user_prompt(question, retrieved)         (contexte + consigne de citation)
  → llm.complete(system, prompt, model, max_tokens)
  → Answer(text, citations, model)                 (grounded = citations non vides)
```

## Gestion des erreurs

Exceptions métier dans `app/domain/exceptions.py`, mappées en codes HTTP
dans `app/presentation/api.py` :

| Exception | HTTP |
|---|---|
| `NoRelevantContextError` | 422 |
| `CourseNotFoundError` | 404 |
| `BudgetExceededError` | 429 |

## Décisions

Les choix structurants sont tracés dans [adr/](adr/).
