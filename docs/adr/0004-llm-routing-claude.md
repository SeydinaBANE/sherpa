# ADR 0004 — LLM : Claude avec routing multi-modèle

- Statut : accepté
- Date : 2026-06-11

## Contexte

Les tâches ont des exigences variables : certaines sont simples et fréquentes
(reformulation, classification), d'autres exigent un raisonnement poussé (diagnostic,
LLM-judge). Optimiser coût et latence est un objectif explicite.

## Décision

Utiliser **Claude** via un routing multi-modèle, configurable par env :

- `claude-haiku-4-5` — tâches simples, cheap & rapide.
- `claude-sonnet-4-6` — réponses RAG standard, génération de quiz.
- `claude-opus-4-8` — raisonnement complexe, LLM-judge.

Embeddings via **Voyage AI** (recommandé par Anthropic).

## Alternatives

- Un seul gros modèle pour tout : plus simple mais coûteux et plus lent.
- Modèles open-source auto-hébergés : moins chers à l'usage mais surcoût opérationnel.

## Conséquences

- Coût/latence optimisés en aiguillant chaque tâche vers le bon modèle.
- Un `LLMPort` unique ; le choix du modèle est un paramètre, pas un couplage.
