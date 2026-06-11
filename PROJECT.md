# PROJECT — Sherpa

## Vision

Donner à chaque étudiant un tuteur IA personnel qui **comprend ses propres supports de cours** et l'aide à réviser efficacement, sans jamais inventer.

## Problème

- Les étudiants se noient dans des PDF, slides et notes hétérogènes.
- Les chatbots génériques **hallucinent** et ne citent pas leurs sources → inutilisables pour réviser sérieusement.
- Réviser efficacement demande de la structure (quoi réviser, quand, où sont mes lacunes).

## Proposition de valeur

Un assistant **ancré dans le corpus du cours**, qui cite ses sources, génère des quiz et un plan de révision, et s'adapte aux lacunes de l'étudiant.

## Personae

- **Étudiant (prépa, licence, master)** : révise un examen, veut des réponses fiables et des exercices.
- **Enseignant** : dépose ses supports, suit la progression agrégée (anonymisée).

## Périmètre (v1)

- Ingestion de documents texte → base de connaissances par cours.
- Q&A RAG ancré avec citations + refus gracieux hors-corpus.
- API REST documentée (OpenAPI).

## Hors périmètre (v1)

- Application mobile / front complet.
- Multi-tenant avec facturation.
- Génération d'images / vidéos.

## Métriques de succès

| Dimension | Métrique | Cible v1 |
|---|---|---|
| Fiabilité | Taux de réponses ancrées (citations) | 100 % |
| Qualité | RAGAS faithfulness | ≥ 0.85 |
| Qualité | RAGAS answer relevancy | ≥ 0.80 |
| Performance | Latence p95 `/ask` | < 3 s |
| Coût | Coût moyen / requête | suivi & budgété |
| Adoption | Questions / étudiant actif / semaine | en hausse |

## Principes produit

1. **Pas de réponse sans source.** En cas de doute, refuser.
2. **Vie privée d'abord** (RGPD, données potentiellement de mineurs).
3. **Mesurable** : chaque changement de qualité est évalué (evals en CI).
