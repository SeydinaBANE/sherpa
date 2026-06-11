# Documentation Sherpa

Index de la documentation technique. Voir aussi le [README](../README.md) racine.

## Conception
- [ARCHITECTURE.md](ARCHITECTURE.md) — couches, ports/adapters, flux RAG, erreurs
- [adr/](adr/) — Architecture Decision Records (Qdrant, LangGraph, routing Claude…)
- [RAG_DESIGN.md](RAG_DESIGN.md) — chunking, retrieval hybride, garde-fous anti-hallucination
- [AGENTS.md](AGENTS.md) — agents + orchestration LangGraph
- [GLOSSARY.md](GLOSSARY.md) — vocabulaire

## Exploitation
- [API.md](API.md) — endpoints (pointe vers l'OpenAPI auto-généré)
- [OBSERVABILITY.md](OBSERVABILITY.md) — métriques, logs, request-id, SLO/SLI
- [RUNBOOK.md](RUNBOOK.md) — incidents & remédiation
- [DEPLOYMENT.md](DEPLOYMENT.md) — environnements, Cloud Run, rollback
- [COST.md](COST.md) — modèle de coûts & garde-fous

## Qualité & conformité
- [EVALS.md](EVALS.md) — méthodologie d'évaluation (golden set, RAGAS, LLM-judge)
- [THREAT_MODEL.md](THREAT_MODEL.md) — surface d'attaque & mitigations
- [DATA_PRIVACY.md](DATA_PRIVACY.md) — RGPD, données étudiants

## Démarrer
- [ONBOARDING.md](ONBOARDING.md) — du clone au premier PR
