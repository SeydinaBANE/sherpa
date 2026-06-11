# Évaluations

## Pourquoi

La qualité d'un système RAG n'est pas garantie par les tests unitaires. On mesure la
qualité **fonctionnelle** sur un jeu de données de référence (golden set), en CI.

## Golden set

`evals/dataset.py` — chaque `EvalCase` contient un document, une question et des
`expected_keywords`. Versionné avec le code (traçabilité de la qualité).

## Runner

`evals/run.py` (lancé par `make evals` et en CI) :

| Métrique | Définition | Seuil v1 |
|---|---|---|
| `grounding` | part de réponses avec citations | 1.00 |
| `keyword_recall` | part de réponses contenant le mot-clé attendu | ≥ 0.50 |

Sortie : `grounding=1.00 keyword_recall=1.00 n=2` + code de sortie non nul si échec
(seuils bloquants en CI).

## LLM-judge ✅

`evals/judge.py` — `LLMJudge` note la **fidélité** d'une réponse au contexte (sortie JSON
validée : `faithful`, `score` 1–5, `rationale`). Runner `evals/judge_run.py` (`make judge`)
évalue le golden set et applique un seuil ; il **s'active avec le backend `anthropic`** et
s'ignore proprement sinon (CI offline reste verte). Logique testée hors-ligne via un faux juge.

## Évolution

- **RAGAS** : answer/context relevancy, recall.
- Dataset enrichi + suivi des régressions par PR.
