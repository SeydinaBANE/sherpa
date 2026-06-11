# Configuration

Toute la configuration passe par des **variables d'environnement** préfixées `SHERPA_`
(12-Factor), chargées par `pydantic-settings` (`app/config.py`). Voir [`.env.example`](../.env.example).

## Application

| Variable | Défaut | Description |
|---|---|---|
| `SHERPA_ENV` | `local` | `local` · `staging` · `production` |
| `SHERPA_LOG_LEVEL` | `INFO` | Niveau de log |
| `SHERPA_API_HOST` | `127.0.0.1` | Hôte d'écoute (le conteneur écoute `0.0.0.0`) |
| `SHERPA_API_PORT` | `8000` | Port d'écoute |

## Backends (commutateurs)

| Variable | Défaut | Valeurs |
|---|---|---|
| `SHERPA_RETRIEVAL_BACKEND` | `memory` | `memory` (in-process) · `hybrid` (Qdrant + BM25) |
| `SHERPA_LLM_BACKEND` | `echo` | `echo` (hors-ligne) · `anthropic` (Claude + résilience + cache) |
| `SHERPA_MEMORY_BACKEND` | `memory` | `memory` · `sql` (SQLAlchemy/Postgres) |
| `SHERPA_CACHE_BACKEND` | `memory` | `memory` · `redis` |

## LLM (Claude) & embeddings

| Variable | Défaut | Description |
|---|---|---|
| `SHERPA_ANTHROPIC_API_KEY` | – | Clé API Anthropic |
| `SHERPA_LLM_MODEL_CHEAP` | `claude-haiku-4-5` | Tâches simples |
| `SHERPA_LLM_MODEL_STANDARD` | `claude-sonnet-4-6` | RAG / quiz / plan |
| `SHERPA_LLM_MODEL_DEEP` | `claude-opus-4-8` | Diagnostic / raisonnement |
| `SHERPA_VOYAGE_API_KEY` | – | Clé API Voyage AI |
| `SHERPA_EMBEDDING_MODEL` | `voyage-3` | Modèle d'embeddings |

## Retrieval & stores

| Variable | Défaut | Description |
|---|---|---|
| `SHERPA_QDRANT_URL` | `http://localhost:6333` | URL Qdrant |
| `SHERPA_QDRANT_COLLECTION` | `sherpa_chunks` | Collection vectorielle |
| `SHERPA_RRF_K` | `60` | Constante de fusion RRF |
| `SHERPA_TOP_K` | `4` | Nombre de chunks récupérés |
| `SHERPA_DATABASE_URL` | `postgresql+psycopg://…` | Postgres (async) |
| `SHERPA_REDIS_URL` | `redis://localhost:6379/0` | Redis (cache, à venir) |

## Coûts & résilience

| Variable | Défaut | Description |
|---|---|---|
| `SHERPA_LLM_CACHE_ENABLED` | `true` | Active le cache des complétions (backend `anthropic`) |
| `SHERPA_LLM_CACHE_TTL_SECONDS` | `3600` | Durée de vie d'une entrée de cache |
| `SHERPA_MAX_TOKENS_PER_REQUEST` | `4096` | Plafond de tokens par appel |
| `SHERPA_DAILY_TOKEN_BUDGET` | `1000000` | Budget quotidien → `429` si dépassé |
| `SHERPA_LLM_MAX_RETRIES` | `3` | Tentatives sur erreur transitoire |
| `SHERPA_LLM_RETRY_BASE_DELAY` | `0.2` | Délai de base (backoff exponentiel) |
| `SHERPA_LLM_TIMEOUT_SECONDS` | `30` | Timeout par appel LLM |
| `SHERPA_BREAKER_FAILURE_THRESHOLD` | `5` | Seuil d'ouverture du circuit breaker |
| `SHERPA_BREAKER_RESET_TIMEOUT` | `30` | Délai avant tentative half-open |

## Observabilité

| Variable | Défaut | Description |
|---|---|---|
| `SHERPA_LANGFUSE_PUBLIC_KEY` | – | Clé publique Langfuse (à venir) |
| `SHERPA_LANGFUSE_SECRET_KEY` | – | Clé secrète Langfuse (à venir) |
| `SHERPA_LANGFUSE_HOST` | `http://localhost:3000` | Hôte Langfuse |

> **Secrets** : jamais en clair dans le dépôt. En production, via un secret manager
> (cf. [SECURITY.md](../SECURITY.md)). Seul `.env.example` est versionné.
