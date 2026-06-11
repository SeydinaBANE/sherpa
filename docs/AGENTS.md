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

## Orchestration LangGraph

`AssistantOrchestrator` (`app/infrastructure/orchestration/assistant.py`) câble les agents
dans un **graphe LangGraph** : un nœud `route` classe l'intention du message
(`classify_intent`) puis des **arêtes conditionnelles** dispatchent vers `tutor`, `quiz` ou
`plan`. Les nœuds réutilisent les services existants (aucune duplication de logique).

```
START → route ──(quiz)→ quiz ─┐
              ──(plan)→ plan ─┼→ END
              ──(tutor)→ tutor┘
```

Exposé via `POST /assistant` ; la réponse porte l'`intent` et le payload de l'agentchoisi.

### Reste à faire
- Checkpointer Postgres pour la **mémoire étudiant** (sessions, suivi des lacunes).
- Routing d'intention par LLM (fallback sur les règles actuelles).

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
