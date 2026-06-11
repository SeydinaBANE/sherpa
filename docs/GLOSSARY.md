# Glossaire

| Terme | Définition |
|---|---|
| **RAG** | Retrieval-Augmented Generation : génération conditionnée par des documents récupérés. |
| **Chunk** | Fragment de document indexé et récupérable. |
| **Ancrage (grounding)** | Le fait qu'une réponse s'appuie sur des sources citées du corpus. |
| **Citation** | Référence `[source:ordinal]` vers le chunk ayant servi à répondre. |
| **Retrieval hybride** | Combinaison recherche dense (vecteurs) + sparse (BM25). |
| **RRF** | Reciprocal Rank Fusion : fusion de classements de plusieurs retrievers. |
| **Reranking** | Reclassement fin des résultats récupérés (souvent cross-encoder). |
| **Embedding** | Représentation vectorielle d'un texte pour la recherche sémantique. |
| **Port** | Interface (`Protocol`) définie par le domaine, implémentée par un adapter. |
| **Adapter** | Implémentation concrète d'un port (in-memory, Qdrant, Claude…). |
| **Routing multi-modèle** | Aiguillage d'une tâche vers le modèle LLM adapté (coût/latence). |
| **Eval** | Évaluation de la qualité fonctionnelle sur un golden set. |
| **RAGAS** | Framework d'évaluation RAG (faithfulness, relevancy…). |
| **LLM-judge** | LLM utilisé pour noter la qualité d'une réponse. |
| **SLO/SLI** | Objectif / indicateur de niveau de service. |
| **Idempotence** | Une opération répétée produit le même état (ré-ingestion = no-op). |
