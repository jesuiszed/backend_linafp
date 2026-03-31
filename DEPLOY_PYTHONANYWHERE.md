# Heberger le backend LINAFP sur PythonAnywhere

Ce document explique toutes les etapes pour deployer le backend FastAPI LINAFP sur PythonAnywhere.

## 1) Prerequis

1. Avoir un compte PythonAnywhere.
2. Avoir le code backend disponible sur PythonAnywhere (git clone ou upload zip).
3. Choisir votre base:
	- Option simple: SQLite local (`.db`) sur PythonAnywhere.
	- Option avancee: PostgreSQL distant (Neon, Supabase, Render, etc.).

Note:
- Le projet supporte SQLite et PostgreSQL via `DATABASE_URL`.
- Pour PythonAnywhere, SQLite est la solution la plus simple a mettre en place.

## 2) Arborescence attendue

Exemple de chemin dans le compte PythonAnywhere:

```bash
/home/<votre_user>/LINAFP/backend
```

## 3) Creer un environnement virtuel

Dans une console Bash PythonAnywhere:

```bash
cd /home/<votre_user>/LINAFP/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Ajouter un adaptateur WSGI pour FastAPI

PythonAnywhere sert principalement du WSGI. FastAPI est ASGI, donc il faut un adaptateur.

Installez `a2wsgi`:

```bash
source /home/<votre_user>/LINAFP/backend/.venv/bin/activate
pip install a2wsgi
```

Creez le fichier `app/wsgi.py`:

```python
from a2wsgi import ASGIMiddleware

from app.main import app as asgi_app

application = ASGIMiddleware(asgi_app)
```

## 5) Configurer les variables d environnement

Option recommandee: creer un fichier `.env` dans le dossier backend.

Exemple minimal:

```env
ENV=production
APP_NAME=LINAFP API
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite:////home/<votre_user>/LINAFP/backend/linafp.db
SECRET_KEY=change-this-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://<votre-frontend>.onrender.com,https://<votre-site>.pythonanywhere.com
```

Important:
- Utiliser une vraie valeur forte pour `SECRET_KEY`.
- Si vous utilisez PostgreSQL distant, verifier que l URL accepte les connexions depuis PythonAnywhere.

## 6) Appliquer les migrations

```bash
cd /home/<votre_user>/LINAFP/backend
source .venv/bin/activate
alembic upgrade head
```

Option seed (si necessaire):

```bash
PYTHONPATH=. python scripts/seed_gabon_2025_2026.py
```

## 7) Creer l application web sur PythonAnywhere

1. Ouvrir l onglet `Web`.
2. Cliquer `Add a new web app`.
3. Choisir `Manual configuration`.
4. Choisir Python 3.11 (ou version compatible).

## 8) Configurer le fichier WSGI de PythonAnywhere

Dans l onglet `Web`, ouvrir le fichier WSGI genere par PythonAnywhere
(ex: `/var/www/<votre_user>_pythonanywhere_com_wsgi.py`) et remplacer son contenu par:

```python
import os
import sys

project_home = '/home/<votre_user>/LINAFP/backend'
if project_home not in sys.path:
		sys.path.insert(0, project_home)

os.environ['PYTHONPATH'] = project_home

from app.wsgi import application
```

## 9) Configurer le virtualenv dans l onglet Web

Dans `Virtualenv`, renseigner:

```text
/home/<votre_user>/LINAFP/backend/.venv
```

## 10) Fichiers statiques (optionnel)

Le backend API n a pas besoin de fichiers statiques pour fonctionner.
Vous pouvez ignorer cette section si vous hebergez seulement l API.

## 11) Recharger l application

Dans l onglet `Web`, cliquer `Reload`.

## 12) Verifications apres deploiement

Tester dans le navigateur:

1. `https://<votre_user>.pythonanywhere.com/api/v1/health`
2. `https://<votre_user>.pythonanywhere.com/docs`

Tester via curl:

```bash
curl -X GET 'https://<votre_user>.pythonanywhere.com/api/v1/health'
```

## 13) Creer le premier admin (si necessaire)

```bash
curl -X POST 'https://<votre_user>.pythonanywhere.com/api/v1/auth/bootstrap-admin' \
	-H 'Content-Type: application/json' \
	-d '{"username":"admin","password":"ChangeMeNow123!"}'
```

Si un admin existe deja, l API renvoie `409`.

## 14) Mise a jour d une nouvelle version

Dans Bash:

```bash
cd /home/<votre_user>/LINAFP/backend
git pull
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

Puis cliquer `Reload` dans l onglet `Web`.

## 15) Depannage

Si erreur 500:

1. Verifier les logs dans l onglet `Web`:
	 - `Error log`
	 - `Server log`
2. Verifier le chemin du virtualenv.
3. Verifier `DATABASE_URL` et l acces reseau a la base.
4. Verifier que `app/wsgi.py` existe et exporte `application`.
5. Verifier que `alembic upgrade head` est bien passe.

### Cas frequent: connection refused sur 127.0.0.1:5432

Si vous voyez cette erreur:

```text
sqlalchemy.exc.OperationalError: connection to server at "127.0.0.1", port 5432 failed: Connection refused
```

Cela veut dire que votre app essaye de se connecter a PostgreSQL local sur PythonAnywhere.
Or il n y a pas de serveur Postgres local actif a cette adresse.

Cause habituelle:
- `DATABASE_URL` n est pas surchargee et la valeur par defaut du projet (`localhost:5432`) est utilisee.

Correction immediate:

1. Ouvrir votre fichier `.env` dans le backend.
2. Remplacer `DATABASE_URL`:
	- soit par SQLite local,
	- soit par une vraie base PostgreSQL distante.
3. Recharger l app web.

Exemple:

```env
DATABASE_URL=sqlite:////home/<votre_user>/LINAFP/backend/linafp.db
```

Alternative PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

Test de connexion depuis Bash PythonAnywhere:

```bash
cd /home/<votre_user>/LINAFP/backend
source .venv/bin/activate
python -c "from app.core.config import settings; print(settings.database_url)"
python -c "from app.db.session import engine; conn = engine.connect(); print('DB OK'); conn.close()"
```

Si le test echoue encore:
- verifier user/password/host/port/dbname,
- verifier que le provider accepte les connexions externes,
- verifier les regles reseau/firewall du provider,
- verifier que votre plan PythonAnywhere autorise la sortie reseau vers ce provider.

### Recommandation finale PythonAnywhere

Pour demarrer vite et eviter les erreurs reseau, utilisez:

```env
DATABASE_URL=sqlite:////home/<votre_user>/LINAFP/backend/linafp.db
```

## 16) Checklist rapide

1. Code backend present sur PythonAnywhere.
2. `.venv` cree + dependances installees.
3. `a2wsgi` installe + `app/wsgi.py` cree.
4. Variables env configurees (`.env`).
5. Migrations appliquees.
6. WSGI PythonAnywhere pointe vers `from app.wsgi import application`.
7. Reload web app effectue.
8. `/api/v1/health` et `/docs` OK.
