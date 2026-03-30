# Backend LINAFP

## Lancer en local
1. Créer un environnement Python.
2. Installer les dépendances:
   - `pip install -r requirements.txt`
3. Copier `.env.example` vers `.env` et ajuster les valeurs.
4. Démarrer le serveur:
   - `uvicorn app.main:app --reload`

## URL utiles
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Migrations Alembic
- Initialiser le schema en base:
   - `alembic upgrade head`
- Creer une nouvelle migration:
   - `alembic revision --autogenerate -m "message"`
- Revenir d'une migration:
   - `alembic downgrade -1`

## Tests minimaux
- Installer les dependances dev:
   - `pip install -r requirements-dev.txt`
- Lancer les tests:
   - `pytest -q`

## Authentification (JWT)
- Creer le premier admin:
   - `POST /api/v1/auth/bootstrap-admin`
   - payload JSON: `{ "username": "admin", "password": "change-me" }`
- Se connecter:
   - `POST /api/v1/auth/login` (form-data OAuth2: `username`, `password`)
- Rafraichir le token:
   - `POST /api/v1/auth/refresh`
- Obtenir le profil courant:
   - `GET /api/v1/auth/me` avec header `Authorization: Bearer <access_token>`

## Matchs et evenements
- Matchs:
   - `GET /api/v1/matches`
   - `POST /api/v1/matches`
   - `GET /api/v1/matches/{match_id}`
   - `PATCH /api/v1/matches/{match_id}`
   - `POST /api/v1/matches/{match_id}/score`
   - `POST /api/v1/matches/{match_id}/lock`
   - `POST /api/v1/matches/{match_id}/unlock`
- Evenements:
   - `GET /api/v1/matches/{match_id}/events`
   - `POST /api/v1/matches/{match_id}/events`
   - `PATCH /api/v1/matches/{match_id}/events/{event_id}`
   - `DELETE /api/v1/matches/{match_id}/events/{event_id}`

## Classement et statistiques
- Classement:
   - `GET /api/v1/standings?season_id=...`
- Statistiques:
   - `GET /api/v1/stats/top-scorers?season_id=...&limit=10`
   - `GET /api/v1/stats/top-assists?season_id=...&limit=10`
   - `GET /api/v1/stats/cards?season_id=...`
   - `GET /api/v1/stats/club-form?season_id=...&club_id=...&last=5`
   - `GET /api/v1/stats/player-summary?season_id=...&player_id=...`

## Audit et controle qualite
- Audit logs (admin):
   - `GET /api/v1/audit-logs`
- Detection incoherences (admin/editor):
   - `GET /api/v1/quality/inconsistencies`
