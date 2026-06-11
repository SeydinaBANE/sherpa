# Agents (Phase 2)

> Cible : orchestration via **LangGraph**. Ce document décrit le design prévu.

## Principe

Un graphe d'états où chaque nœud est un agent outillé. Le retrieval RAG est un outil
partagé. La mémoire étudiant est persistée (checkpointer Postgres) pour l'adaptation.

## Agents

| Agent | Rôle | Modèle (routing) |
|---|---|---|
| `tutor` | Q&A pédagogique ancré (RAG) | sonnet |
| `quiz_generator` | Génère un quiz depuis le corpus | sonnet |
| `study_planner` | Construit un plan de révision | sonnet |
| `weakness_diagnoser` | Identifie les lacunes via l'historique | opus |

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

- Chaque agent qui répond sur le fond passe par le retrieval ancré.
- Budgets de tokens par exécution de graphe (voir [COST.md](COST.md)).
