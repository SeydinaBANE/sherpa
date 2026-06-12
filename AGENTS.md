# Sherpa — Agent instructions

Single-module Python package (>=3.11, Hatchling). FastAPI app with Clean Architecture.

## Dev commands

```sh
make install     # create venv + pip install -e ".[dev]" + pre-commit install
make dev         # python -m app.main (reload on, prod off)
make lint        # ruff check app tests evals
make format      # ruff format + ruff check --fix app tests evals
make typecheck   # mypy app (--strict)
make test        # pytest
make cov         # pytest --cov=app --cov-report=term-missing
make evals       # python -m evals.run (RAG golden set — runs in CI, blocking)
make judge       # python -m evals.judge_run (skips if backend != anthropic)
make migrate     # alembic upgrade head
make up          # docker compose up -d --build (qdrant + postgres + redis + api)
make precommit   # pre-commit run --all-files
```

CI pipeline order: lint → format check → typecheck → bandit → test+cov → evals.

## Architecture

```
app/domain/         entities, ports (Protocol), exceptions
app/application/    use-cases: rag/service.py, agents/ (quiz, planner, diagnoser), ingestion/
app/infrastructure/ adapters: retrieval/, llm/, cache/, persistence/, resilience/, orchestration/
app/presentation/   FastAPI app, routers, schemas, middleware, security, dependencies.py
```

Composition root is `app/presentation/dependencies.py` — `lru_cache` singletons wired from env.
Inversion of dependency: domain defines `typing.Protocol` ports; infra provides concrete adapters.

## Defaults (no external services needed)

- `RetrievalBackend.MEMORY` → `InMemoryRetriever` (TF-IDF)
- `LLMBackend.ECHO` → `EchoLLM` (deterministic, no network)
- `MemoryBackend.MEMORY` → `InMemoryStudyMemory`
- `CacheBackend.MEMORY` → `InMemoryCache`
- Auth/rate-limit/quota all disabled by default

Most tests work offline with these defaults. Production backends (Qdrant, Anthropic, SQL, Redis) activated by setting `SHERPA_*` env vars.

## Config

All env vars prefixed `SHERPA_`, loaded via pydantic-settings from `.env`. See `app/config.py:Settings`.

## Testing quirks

- `asyncio_mode = auto` — test functions are async by default.
- `filterwarnings = ["error"]` — any warning fails the test.
- `conftest.py` clears all `lru_cache` singletons before/after each test (`autouse` fixture).
- API tests use `httpx.AsyncClient` with `ASGITransport` (no server needed).
- Coverage floor: 70% (`fail_under=70`).
- Tests use mocks / in-memory adapters, not real services.

## Code style

- Ruff line-length=100, target=py311. Rule set: E, F, I, N, UP, B, C4, SIM, RUF.
- `S101` (assert) allowed in tests only.
- mypy: strict mode, pydantic plugin, several third-party libs ignored.
- Pre-commit hooks: trailing-whitespace, end-of-file-fixer, ruff (fix+format), mypy (app/), bandit (skip tests/), gitleaks, conventional-commit (commit-msg stage).
- Commit messages must follow conventional commits format.

## Key docs

- `docs/ARCHITECTURE.md` — layers, RAG flow, error handling
- `docs/AGENTS.md` — agent design, LangGraph orchestration
- `docs/API.md` — endpoint reference
- `docs/RAG_DESIGN.md` — chunking, retrieval, anti-hallucination
- `docs/CONFIGURATION.md` — all env vars reference
- `docs/TESTING.md` — testing strategy
- `docs/EVALS.md` — eval methodology
