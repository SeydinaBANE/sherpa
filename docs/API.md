# API

La spécification OpenAPI est générée automatiquement par FastAPI :

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`
- Schéma JSON : `http://localhost:8000/openapi.json`

## Endpoints

### `GET /healthz`
Sonde de vivacité. Réponse : `{ "status": "ok", "version": "...", "environment": "local" }`.

### `GET /metrics`
Métriques Prometheus (text/plain) : `sherpa_http_requests_total`,
`sherpa_http_request_duration_seconds`. Toutes les réponses portent un en-tête `X-Request-ID`.

### `POST /ingest`
Indexe un document dans le corpus d'un cours.

```json
{ "course_id": "bio", "source": "cours.pdf", "text": "..." }
```
Réponse `201` : `{ "course_id": "bio", "chunks_created": 3 }`.
Ré-ingérer un contenu identique renvoie `chunks_created: 0` (idempotence).

### `POST /ingest/file`
Indexe un fichier uploadé (`multipart/form-data`).

- Champ `course_id` (form) + champ `file` (`.pdf`, `.txt`, `.md`).
- Réponse `201` : `{ "course_id": "bio", "chunks_created": 5 }`.
- `415` si le type de fichier n'est pas supporté.

```bash
curl -X POST localhost:8000/ingest/file \
  -F course_id=bio -F file=@cours.pdf
```

### `POST /ask`
Pose une question, réponse ancrée avec citations.

```json
{ "course_id": "bio", "question": "Que fait la photosynthèse ?" }
```
Réponse `200` :
```json
{
  "answer": "...",
  "model": "claude-sonnet-4-6",
  "grounded": true,
  "citations": [{ "source": "cours.pdf", "ordinal": 0, "snippet": "..." }]
}
```
`422` si aucun contexte pertinent (refus gracieux).

## Agents

### `POST /agents/quiz`
`{ "course_id": "bio", "topic": "photosynthèse", "num_questions": 5 }` →
`{ "course_id", "topic", "questions": [{ "question", "choices", "answer_index", "explanation" }] }`.

### `POST /agents/study-plan`
`{ "course_id": "bio", "topic": "photosynthèse", "days": 7 }` →
`{ "course_id", "items": [{ "day", "topic", "activities": [...] }] }`.

### `POST /agents/diagnose`
`{ "course_id": "bio", "answers": [{ "question": "...", "correct": false }] }` →
`{ "course_id", "weak_topics": [...], "recommendation": "..." }`.

> Les agents nécessitent un corpus indexé (sinon `422`) et le backend LLM `anthropic`
> pour des sorties utiles ; une sortie LLM non conforme renvoie `502`.

### `POST /assistant`
Orchestration LangGraph : route un message libre vers l'agent adapté.

`{ "course_id": "bio", "message": "Donne-moi un quiz sur la photosynthèse" }` →
`{ "intent": "quiz", "answer": null, "quiz": {...}, "plan": null }`.

`intent` ∈ `tutor` | `quiz` | `plan` ; seul le champ correspondant est renseigné.

### `POST /agents/diagnose-from-history`
`{ "student_id": "s1", "course_id": "bio" }` → diagnostic basé sur l'historique stocké
(`404` si aucun historique).

## Mémoire étudiant

### `POST /memory/answers`
`{ "student_id": "s1", "course_id": "bio", "answers": [{ "question": "...", "correct": false }] }`
→ `201 { "recorded": 1 }`.

### `GET /memory/history?student_id=s1&course_id=bio`
→ `{ "student_id", "course_id", "events": [{ "question", "correct", "created_at" }] }`.

## Codes d'erreur

| Code | Signification |
|---|---|
| 415 | Type de fichier non supporté (`/ingest/file`) |
| 422 | Aucun contexte pertinent (`NoRelevantContextError`) |
| 404 | Cours introuvable (`CourseNotFoundError`) |
| 429 | Budget de tokens dépassé (`BudgetExceededError`) |
| 502 | Sortie d'agent LLM invalide (`AgentOutputError`) |
