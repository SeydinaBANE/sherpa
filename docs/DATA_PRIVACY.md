# Confidentialité des données (RGPD)

L'éducation implique des données personnelles, **potentiellement de mineurs**. La
protection des données est un principe produit, pas une option.

## Principes

- **Minimisation** : ne collecter que le nécessaire (supports de cours, historique de révision).
- **Finalité** : usage strictement pédagogique ; pas de revente, pas de profilage publicitaire.
- **Base légale** : consentement (et autorisation parentale pour les mineurs).
- **Localisation** : hébergement et traitement dans l'UE.

## Droits des personnes

- **Accès / portabilité** : export des données d'un étudiant sur demande.
- **Rectification** : correction des données inexactes.
- **Effacement** : `DELETE /courses/{course_id}` supprime les vecteurs (retriever) et les
  métadonnées de chunks ; `DELETE /students/{student_id}` supprime tout l'historique de
  l'étudiant (`study_events`).
- **Limitation / opposition** : selon les cas.

## Mesures techniques

- Chiffrement en transit (TLS) et au repos (volumes/DB chiffrés).
- Pseudonymisation des identifiants dans les logs ; pas de PII en clair dans les traces.
- Rétention bornée (durée à définir par finalité), purge automatisée.
- Contrôle d'accès (auth JWT, RBAC à venir), journalisation des accès.

## Sous-traitants

- Fournisseurs LLM/embeddings : vérifier l'absence d'entraînement sur les données et la
  conformité (DPA, localisation). Documenter dans le registre des traitements.

## Registre des traitements

À maintenir : finalités, catégories de données, durées de conservation, destinataires.
