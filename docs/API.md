# API

La spécification OpenAPI est générée automatiquement par FastAPI :

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`
- Schéma JSON : `http://localhost:8000/openapi.json`

## Endpoints

### `GET /healthz`
Sonde de vivacité. Réponse : `{ "status": "ok", "version": "...", "environment": "local" }`.

### `POST /ingest`
Indexe un document dans le corpus d'un cours.

```json
{ "course_id": "bio", "source": "cours.pdf", "text": "..." }
```
Réponse `201` : `{ "course_id": "bio", "chunks_created": 3 }`.
Ré-ingérer un contenu identique renvoie `chunks_created: 0` (idempotence).

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

## Codes d'erreur

| Code | Signification |
|---|---|
| 422 | Aucun contexte pertinent (`NoRelevantContextError`) |
| 404 | Cours introuvable (`CourseNotFoundError`) |
| 429 | Budget de tokens dépassé (`BudgetExceededError`) |
