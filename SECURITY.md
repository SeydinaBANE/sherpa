# Politique de sécurité

## Signaler une vulnérabilité

Merci de **ne pas** ouvrir d'issue publique pour une faille de sécurité.
Contacte l'équipe en privé : `security@sherpa.example`.
Nous accusons réception sous 72 h et visons un correctif sous 30 jours.

## Gestion des secrets

- Aucun secret en clair dans le dépôt (clés API, mots de passe, tokens).
- Configuration via variables d'environnement / secret manager (GCP/AWS).
- `gitleaks` et `detect-private-key` s'exécutent en pre-commit et en CI.
- `.env` est ignoré par git ; seul `.env.example` est versionné.

## Dépendances

- `dependabot` ouvre des PR hebdomadaires (pip, actions, docker).
- `bandit` (SAST) s'exécute en CI sur `app/`.
- **Trivy** scanne l'image Docker en CI (échec sur HIGH/CRITICAL corrigeables).
- Recommandé en complément : `pip-audit`.

## Surface LLM

- Mitigations contre l'injection de prompt et l'exfiltration de contexte
  (voir [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)).
- Validation stricte des entrées (Pydantic), quotas et budgets de tokens.

## Données personnelles

Le traitement des données étudiants suit [docs/DATA_PRIVACY.md](docs/DATA_PRIVACY.md) (RGPD).
