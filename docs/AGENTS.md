# Agents (Phase 2)

## Principe

Les **agents sont des services de la couche application** (`app/application/agents/`) qui
s'appuient sur les ports (`RetrieverPort`, `LLMPort`) : ils sont donc testables hors-ligne.
Chaque agent (1) ancre sa réponse via le retrieval, (2) demande au LLM une sortie **JSON
structurée**, (3) la valide en modèle Pydantic (`parse_model`). Une sortie LLM invalide
lève `AgentOutputError` → HTTP 502.

## Agents (implémentés)

| Agent | Rôle | Modèle (routing) | Endpoint |
|---|---|---|---|
| `tutor` (RAG) | Q&A pédagogique ancré | sonnet | `POST /ask` |
| `QuizGenerator` | Quiz QCM depuis le corpus | sonnet | `POST /agents/quiz` |
| `StudyPlanner` | Plan de révision jour par jour | sonnet | `POST /agents/study-plan` |
| `WeaknessDiagnoser` | Lacunes + recommandation | opus | `POST /agents/diagnose` |

## Orchestration LangGraph (prochaine itération)

La logique métier des agents étant isolée et testée, l'étape suivante est de les **câbler
dans un graphe LangGraph** (routing + état partagé + checkpointer Postgres pour la mémoire
étudiant). Le graphe sera un adapter d'infrastructure qui réutilise ces services tels quels.

## Graphe (esquisse)

```
        ┌──────────┐
input → │ router   │ → tutor ─────────────┐
        └──────────┘ → quiz_generator ────┤→ aggregate → output
                     → study_planner ─────┤
                     → weakness_diagnoser ─┘
```

## Mémoire

- État conversationnel + profil de maîtrise par chapitre.
- Checkpointer Postgres : reprise de session, traçabilité.

## Garde-fous

- Chaque agent passe par le retrieval ancré (`retrieve_context`) ; pas de corpus → 422.
- Sortie LLM strictement validée (Pydantic) ; sortie invalide → 502 (`AgentOutputError`).
- Budgets de tokens par exécution (voir [COST.md](COST.md)).
