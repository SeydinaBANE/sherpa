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
| 9 | LLM-judge présent ; RAGAS restant | 🟡 | 🟡 | partiel |
| 10 | Cache LLM + embeddings en place | 🟢 | — | fait |
| 11 | Graphe LangGraph compilé une fois (mémoïsé) | 🟢 | — | fait |
| 12 | Golden set d'évaluation trop petit (2 cas) | 🟡 | 🟢 | à faire |
| 13 | ResourceWarnings en test (socket non fermé) | 🟢 | 🟢 | à faire |

## Dette résolue

Les items suivants ont été corrigés et ne sont plus de la dette active :

| # | Sujet | Résolu dans |
|---|---|---|
| A | Health check shallow — ne vérifiait aucun backend externe | PR #22 |
| B | Pas de graceful shutdown (lifespan, dispose engines) | PR #22 |
| C | Auth/rate-limit/quota désactivés par défaut, même en prod | PR #22 |
| D | Migration manuelle — pas d'auto-migration au démarrage | PR #22 |
| E | Pytest warning `asyncio_default_fixture_loop_scope` manquant | PR #23 |
| F | `alembic.command.upgrade` synchrone bloquait l'event loop | PR #23 |
| G | `_engines: list` accumulait des engines entre les tests | PR #23 |
| H | Health check créait une engine éphémère à chaque appel | PR #23 |

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
**Authentification par clé API** (`X-API-Key`) et **rate-limiting** en place, activés
automatiquement en production (`env=production`). Limites restantes : pas d'**autorisation
fine** (un porteur de clé accède à tous les cours/étudiants ; `student_id`/`course_id`
restent de confiance) ; le rate-limiter est **par processus** (non distribué).
→ RBAC + scoping des ressources + JWT, rate-limit partagé (Redis).
Cf. [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

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
`evals/` mesure `grounding` + `keyword_recall` (offline) et fournit un **LLM-judge**
(`make judge`, actif sous `anthropic`). Reste : **RAGAS** (answer/context relevancy, recall)
et l'intégration en CI sur clés réelles. → cf. [EVALS](docs/EVALS.md).

### 10 · Cache
Cache des **complétions LLM** (`CachingLLM`) et des **embeddings** (`CachingEmbedding`) en
place (in-memory/Redis). Reste à **mesurer le gain** sous charge réelle
(cf. [COST](docs/COST.md), [PERFORMANCE](docs/PERFORMANCE.md)).

### 11 · Compilation du graphe ✅
`get_assistant_orchestrator` est mémoïsé (`lru_cache`) : le graphe LangGraph est compilé
une seule fois par processus (réinitialisé entre tests via le `conftest`).

### 12 · Golden set d'évaluation trop petit
Seulement 2 cas de test (biology, history) dans `evals/dataset.py`. Trop faible pour
détecter des régressions fines. → Ajouter des cas couvrant les échecs retrieval,
les biais de format, les questions multi-sauts.

### 13 · ResourceWarnings en test
Python 3.11 + Pydantic + Protocols génère des `ResourceWarning: unclosed socket` dans
certains tests. Le projet utilise `filterwarnings = ["error"]`, ce qui les transforme en
erreurs. Solution : ajouter un filtre dans `pyproject.toml` ou dans `conftest.py`.

## Principe

Ces compromis sont **intentionnels et documentés** : le produit est fonctionnel et testé
hors-ligne, et chaque axe de production s'active par configuration sans réécriture
(architecture en ports/adapters).
