# Contribuer à Sherpa

Merci de contribuer 🙌. Ce guide décrit le workflow et les standards.

## Mise en route

```bash
make install        # venv + dépendances + hooks pre-commit
cp .env.example .env
make test
```

## Workflow git

- Branche par défaut stable : `main`. Branche d'intégration : `develop`.
- Crée une branche depuis `develop` : `feat/<sujet>`, `fix/<sujet>`, `docs/<sujet>`.
- Ouvre une PR vers `develop`. La CI doit être verte, une review est requise.

## Conventions de commit (Conventional Commits)

Format : `type(scope): sujet`

Types : `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`.

Exemples :
```
feat(rag): add hybrid retrieval with RRF fusion
fix(api): return 422 when course corpus is empty
docs(adr): record choice of Qdrant over pgvector
```

Le hook `conventional-pre-commit` valide le message au `commit-msg`.

## Standards de code

- Typage strict partout (`mypy --strict`), types concrets (pas d'`Any`).
- Pas de commentaires superflus : le code doit être auto-documenté.
- Respect des couches (pas d'appel infra dans le domaine, etc.).
- Exceptions métier levées dans le domaine, catchées en présentation.
- Config via env (`pydantic-settings`), zéro secret en dur.

## Avant de pousser

```bash
make lint        # ruff
make typecheck   # mypy --strict
make test        # pytest
make evals       # golden set
make precommit   # tous les hooks
```

## Tests

- Au minimum : un cas nominal + un cas d'erreur.
- Nommage : `test_<fonction>_<cas>`.
- Mocker les services externes (LLM, DB, API).
