# Onboarding — Jour 1

Bienvenue 👋. Objectif : du clone au premier PR en moins d'une heure.

## 1. Pré-requis

- Python 3.11, Docker, Make, git.

## 2. Installer

```bash
git clone <repo> && cd sherpa
make install        # venv + dépendances + hooks pre-commit
cp .env.example .env
```

## 3. Vérifier que tout passe

```bash
make lint
make typecheck
make test
make evals
```

## 4. Lancer en local

```bash
make dev            # http://localhost:8000/docs
```

Teste le flux : `POST /ingest` puis `POST /ask` (voir [README](../README.md)).

## 5. Comprendre le code

- Architecture : [ARCHITECTURE.md](ARCHITECTURE.md) et les [ADR](adr/).
- Cœur RAG : `app/application/rag/` + [RAG_DESIGN.md](RAG_DESIGN.md).
- Ports/adapters : `app/domain/ports.py`, `app/infrastructure/`.

## 6. Premier changement

- Branche depuis `develop` : `git switch -c feat/mon-sujet`.
- Code + test (un cas nominal + un cas d'erreur).
- `make precommit`, commit en Conventional Commits, ouvre une PR vers `develop`.

## 7. Où demander de l'aide

- Glossaire : [GLOSSARY.md](GLOSSARY.md).
- Contribution : [CONTRIBUTING.md](../CONTRIBUTING.md).
