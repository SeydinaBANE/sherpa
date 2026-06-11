# Dette technique

Registre **honnête** des compromis assumés et limites connues de Sherpa. Tenu à jour à
chaque évolution. Voir aussi [TODO.md](TODO.md) (backlog) et [ROADMAP.md](ROADMAP.md).

> Légende impact/effort : 🟢 faible · 🟡 moyen · 🔴 élevé.

## Synthèse priorisée

| # | Sujet | Impact | Effort | Statut |
|---|---|---|---|---|
| 1 | Pas de tests d'intégration Qdrant (réseau) | 🟡 | 🟡 | à faire |
| 2 | État applicatif **mono-process** (défauts in-memory) | 🔴 | 🟡 | par design (dev) |
| 3 | AuthN (clé API) + rate-limit en place ; pas d'autorisation fine | 🟡 | 🟡 | partiel |
| 4 | Budget tokens approximatif & non distribué | 🟡 | 🟡 | à faire |
| 5 | Métadonnées de chunks persistées + effacement RGPD | 🟢 | — | fait |
| 6 | Pas de reranking cross-encoder | 🟡 | 🟡 | à faire |
| 7 | Routing d'intention par mots-clés | 🟢 | 🟢 | à faire |
| 8 | Observabilité partielle (pas de Langfuse/Grafana) | 🟡 | 🟡 | à faire |
| 9 | Evals légères (pas de RAGAS/LLM-judge) | 🟡 | 🟡 | à faire |
| 10 | Cache LLM + embeddings en place | 🟢 | — | fait |
| 11 | Graphe LangGraph compilé une fois (mémoïsé) | 🟢 | — | fait |

## Détail

### 1 · Tests d'intégration Qdrant
`QdrantRetriever` n'est couvert que par des tests unitaires de mapping (`to_payload`/
`from_payload`) et de logique via faux client. Le chemin réseau réel n'est pas testé.
→ Ajouter un test `testcontainers` (Qdrant éphémère) marqué `integration`, lancé en CI.

### 2 · État mono-process
Les backends **par défaut** (`InMemoryRetriever`, `EchoLLM`, `InMemoryStudyMemory`) et le
sparse du `HybridRetriever` vivent en mémoire de processus : non partagés entre instances.
**Assumé pour le dev/démo.** En production, basculer sur `qdrant`/`anthropic`/`sql`
(stateless) via `SHERPA_*_BACKEND`.

### 3 · Authentification / autorisation
**Authentification par clé API** (`X-API-Key`) et **rate-limiting** en place (off par défaut,
activables par config). Limites restantes : pas d'**autorisation fine** (un porteur de clé
accède à tous les cours/étudiants ; `student_id`/`course_id` restent de confiance) ; le
rate-limiter est **par processus** (non distribué). → RBAC + scoping des ressources + JWT,
rate-limit partagé (Redis). Cf. [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

### 4 · Budget de tokens
`DailyTokenBudget` charge le **plafond `max_tokens`** (réservation), pas la consommation
réelle ; compteur **en mémoire par processus**, remis à zéro au redémarrage et non partagé.
→ Compter les tokens réellement consommés + backend partagé (Redis) pour le multi-instance.

### 5 · Métadonnées de chunks
Persistées dans `chunk_meta` (`ChunkMetadataPort` + adapters in-memory/SQL, migration 0002).
`DELETE /courses/{id}` supprime vecteurs + métadonnées (droit à l'effacement RGPD).
*Restant* : la suppression côté Qdrant est best-effort (compte non remonté).

### 6 · Reranking
Le retrieval hybride s'arrête à la fusion RRF ; pas de reranking cross-encoder.
→ Étape de reranking optionnelle derrière un port.

### 7 · Routing d'intention
`classify_intent` est basé sur des mots-clés (déterministe, testable, mais limité).
→ Fallback LLM pour les formulations ambiguës.

### 8 · Observabilité
Métriques Prometheus + logs corrélés en place ; **Langfuse** (traces LLM/coûts) et
**Grafana/alerting/SLO** non câblés. → Phase 3 (cf. [OBSERVABILITY](docs/OBSERVABILITY.md)).

### 9 · Évaluations
`evals/` mesure `grounding` + `keyword_recall`. Pas encore de RAGAS (faithfulness, answer/
context relevancy) ni de LLM-judge. → cf. [EVALS](docs/EVALS.md).

### 10 · Cache
Cache des **complétions LLM** (`CachingLLM`) et des **embeddings** (`CachingEmbedding`) en
place (in-memory/Redis). Reste à **mesurer le gain** sous charge réelle
(cf. [COST](docs/COST.md), [PERFORMANCE](docs/PERFORMANCE.md)).

### 11 · Compilation du graphe ✅
`get_assistant_orchestrator` est mémoïsé (`lru_cache`) : le graphe LangGraph est compilé
une seule fois par processus (réinitialisé entre tests via le `conftest`).

## Principe

Ces compromis sont **intentionnels et documentés** : le produit est fonctionnel et testé
hors-ligne, et chaque axe de production s'active par configuration sans réécriture
(architecture en ports/adapters).
