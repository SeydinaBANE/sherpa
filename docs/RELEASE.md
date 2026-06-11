# Processus de release

## Branches

- `main` : branche stable (par défaut). Chaque commit correspond à un état publiable.
- `develop` : intégration continue des features.
- Features : `feat/…`, `fix/…`, `docs/…` depuis `develop`.

## Versionnage

[Semantic Versioning](https://semver.org/lang/fr/) :
- **MAJOR** : changement incompatible.
- **MINOR** : nouvelles fonctionnalités rétrocompatibles.
- **PATCH** : corrections rétrocompatibles.

La version est portée par `pyproject.toml` (`project.version`) et `app/__init__.py`
(`__version__`) — garder les deux synchronisés.

## Étapes

1. S'assurer que `develop` est vert (`make lint typecheck test evals`).
2. **Bump** de version (`pyproject.toml` + `app/__init__.py`).
3. Mettre à jour [CHANGELOG.md](../CHANGELOG.md) : déplacer `Unreleased` vers la nouvelle
   version datée (format *Keep a Changelog*), ajouter les liens de comparaison.
4. Commit `chore(release): vX.Y.Z` sur `develop`, puis push.
5. Ouvrir une **PR `develop → main`**, CI verte, review, puis merge.
6. Créer la **release + tag** : `gh release create vX.Y.Z --target main`.

## Commandes

```bash
# après bump + changelog + merge dans main
gh release create v0.3.0 --target main --title "v0.3.0" --notes "…"
```

## Historique

- **v0.2.0** — RAG production, agents, orchestration LangGraph, mémoire, observabilité, résilience.
- **v0.1.0** — Fondations (Phase 0).
