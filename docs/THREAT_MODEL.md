# Modèle de menaces

## Actifs à protéger

- Données étudiants (documents, historique) — voir [DATA_PRIVACY.md](DATA_PRIVACY.md).
- Clés API (LLM, embeddings) et secrets d'infrastructure.
- Intégrité des réponses (pas de contenu malveillant injecté).

## Surface & menaces

### Injection de prompt
- **Risque** : un document ingéré contient des instructions cachées détournant le modèle.
- **Mitigations** : séparation stricte contexte/consigne, system prompt verrouillé,
  refus hors-source, pas d'exécution d'instructions issues du contexte.

### Exfiltration de contexte / fuite inter-cours
- **Risque** : un utilisateur accède au corpus d'un autre cours/étudiant.
- **Mitigations** : filtrage par `course_id` au retrieval, contrôle d'accès, isolation des index.

### Abus / coûts
- **Risque** : usage massif pour épuiser le budget LLM.
- **Mitigations** : rate limiting, quotas, budgets de tokens (429).

### Secrets
- **Risque** : fuite de clés dans le dépôt ou les logs.
- **Mitigations** : `gitleaks`/`detect-private-key` (pre-commit + CI), secret manager,
  pas de secret dans les logs.

### Chaîne d'approvisionnement
- **Risque** : dépendance compromise.
- **Mitigations** : Dependabot, `bandit`, scan d'image (Trivy), lockfile.

## Validation des entrées

Toutes les entrées API sont validées par Pydantic (longueurs bornées, types stricts).
