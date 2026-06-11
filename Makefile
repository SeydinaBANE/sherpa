.DEFAULT_GOAL := help
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help install dev lint format typecheck test cov evals precommit up down logs clean

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Crée le venv et installe les dépendances de dev
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(VENV)/bin/pre-commit install

dev: ## Lance l'API en local (reload)
	$(PY) -m app.main

lint: ## Lint (ruff)
	$(VENV)/bin/ruff check app tests evals

format: ## Formate le code (ruff)
	$(VENV)/bin/ruff format app tests evals
	$(VENV)/bin/ruff check --fix app tests evals

typecheck: ## Vérifie les types (mypy --strict)
	$(VENV)/bin/mypy app

test: ## Lance les tests
	$(VENV)/bin/pytest

cov: ## Lance les tests avec couverture
	$(VENV)/bin/pytest --cov=app --cov-report=term-missing

evals: ## Lance les évaluations RAG (golden set)
	$(PY) -m evals.run

precommit: ## Lance tous les hooks pre-commit
	$(VENV)/bin/pre-commit run --all-files

up: ## Démarre la stack docker (qdrant, postgres, redis, api)
	docker compose up -d --build

down: ## Arrête la stack docker
	docker compose down

logs: ## Suit les logs de l'API
	docker compose logs -f api

clean: ## Supprime les caches
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
