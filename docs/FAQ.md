# FAQ

### Ça marche sans clé API ?
Oui. Par défaut (`SHERPA_LLM_BACKEND=echo`, `SHERPA_RETRIEVAL_BACKEND=memory`,
`SHERPA_MEMORY_BACKEND=memory`), tout tourne **hors-ligne** avec des adapters déterministes.
Aucune clé n'est requise pour développer, tester ou faire la démo.

### Comment activer la vraie IA (Claude + Qdrant) ?
Renseigner les clés (`SHERPA_ANTHROPIC_API_KEY`, `SHERPA_VOYAGE_API_KEY`) puis passer
`SHERPA_LLM_BACKEND=anthropic` et `SHERPA_RETRIEVAL_BACKEND=hybrid`. Voir
[CONFIGURATION](CONFIGURATION.md). Installer les extras : `pip install ".[rag,data,agents]"`.

### Pourquoi des réponses parfois en « refus » ?
Sherpa ne répond **que** depuis le corpus du cours. Sans contexte pertinent, il renvoie
`422` plutôt que d'inventer (garde-fou anti-hallucination, cf. [RAG_DESIGN](RAG_DESIGN.md)).

### Quelle différence entre `/ask`, `/assistant` et `/agents/*` ?
- `/ask` : Q&A RAG simple.
- `/agents/quiz|study-plan|diagnose` : agents dédiés.
- `/assistant` : orchestrateur LangGraph qui **route** un message libre vers le bon agent.

### Le modèle hallucine / sort un JSON invalide ?
Les agents valident la sortie LLM (Pydantic) ; une sortie non conforme renvoie `502`
(`AgentOutputError`). Voir [AGENTS](AGENTS.md).

### Pourquoi LangGraph / Qdrant / Voyage ?
Choix tracés dans les [ADR](adr/).

### Comment maîtriser les coûts ?
Routing multi-modèle + plafonds et budget de tokens (`429` si dépassé). Voir [COST](COST.md).

### Données personnelles / RGPD ?
Voir [DATA_PRIVACY](DATA_PRIVACY.md).
