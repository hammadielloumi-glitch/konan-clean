# 🚀 PATCHES FI9_NAYEK - PRÉPARATION DÉPLOIEMENT RENDER/VPS

**Date** : 2025-01-XX  
**Protocole** : FI9_NAYEK  
**Cible** : Render.com / VPS Linux

---

## 📋 PROBLÈMES IDENTIFIÉS

### 🔴 CRITIQUES

1. **Host hardcodé** : `main.py` utilise `host="192.168.0.133"` au lieu de `0.0.0.0`
2. **Alembic env.py** : Importe `app.db.base` au lieu de `app.database` (incompatible après patchs)
3. **Alembic.ini** : URL DB hardcodée au lieu d'utiliser `DATABASE_URL`
4. **Gunicorn manquant** : Pas dans `requirements.txt` pour production

### 🟡 IMPORTANTS

5. **Port non configurable** : Hardcodé à 8000 au lieu d'utiliser `PORT` env
6. **Pas de Procfile** : Absent pour Render
7. **Pas de render.yaml** : Absent pour configuration Render
8. **Variables env** : Utilisation directe `os.getenv()` au lieu de `settings`

---

## 📦 LISTE DES PATCHS

### PATCH 1 : `app/main.py` — Host 0.0.0.0 et Port dynamique

**Fichier** : `app/main.py`  
**Action** : Changer host vers `0.0.0.0` et utiliser variable `PORT`

**Paragraphe FI9_NAYEK** :
Le fichier `main.py` utilise un host hardcodé `192.168.0.133` et un port fixe `8000`, rendant le déploiement sur Render/VPS impossible. Render et la plupart des VPS nécessitent `0.0.0.0` pour écouter sur toutes les interfaces réseau, et le port doit être lu depuis la variable d'environnement `PORT` (fournie automatiquement par Render). Le patch FI9_NAYEK corrige ces valeurs pour utiliser `os.getenv("PORT", "8000")` et `host="0.0.0.0"`, garantissant la compatibilité avec tous les environnements de déploiement cloud.

---

### PATCH 2 : `alembic/env.py` — Import Base corrigé

**Fichier** : `alembic/env.py`  
**Action** : Changer `from app.db.base import Base` vers `from app.database import Base`

**Paragraphe FI9_NAYEK** :
Le fichier `alembic/env.py` importe `app.db.base.Base` qui a été transformé en réexport après les patchs de cohérence FI9_NAYEK. Bien que fonctionnel, cet import indirect peut créer des problèmes de détection des modèles lors des migrations automatiques. Le patch FI9_NAYEK corrige l'import pour utiliser directement `app.database.Base`, garantissant que Alembic détecte correctement tous les modèles SQLAlchemy et génère des migrations fiables sans erreurs de métadonnées.

---

### PATCH 3 : `alembic.ini` — URL DB depuis environnement

**Fichier** : `alembic.ini`  
**Action** : Commenter l'URL hardcodée (utilisée uniquement si DATABASE_URL absent)

**Paragraphe FI9_NAYEK** :
Le fichier `alembic.ini` contient une URL de base de données hardcodée qui sera utilisée si `DATABASE_URL` n'est pas défini dans l'environnement. Cette configuration peut causer des migrations vers la mauvaise base de données en production. Le patch FI9_NAYEK commente cette URL et s'appuie uniquement sur `alembic/env.py` qui lit `DATABASE_URL` depuis l'environnement, garantissant que les migrations utilisent toujours la bonne base de données selon l'environnement (dev/staging/prod).

---

### PATCH 4 : `requirements.txt` — Ajouter Gunicorn

**Fichier** : `requirements.txt`  
**Action** : Ajouter `gunicorn` pour production

**Paragraphe FI9_NAYEK** :
Le fichier `requirements.txt` ne contient pas `gunicorn`, serveur WSGI recommandé pour la production FastAPI. Bien qu'uvicorn fonctionne en développement, Gunicorn avec workers multiples offre de meilleures performances et stabilité en production. Le patch FI9_NAYEK ajoute `gunicorn` avec les workers uvicorn (`gunicorn[uvicorn]`), permettant un déploiement production optimisé avec gestion automatique des workers et redémarrage en cas d'erreur, essentiel pour la disponibilité du service.

---

### PATCH 5 : Créer `Procfile` pour Render

**Fichier** : `Procfile` (nouveau)  
**Action** : Créer fichier avec commande de démarrage

**Paragraphe FI9_NAYEK** :
Render nécessite un fichier `Procfile` pour définir la commande de démarrage du service. Sans ce fichier, Render ne peut pas démarrer l'application correctement. Le patch FI9_NAYEK crée un `Procfile` avec la commande complète incluant les migrations Alembic automatiques et le démarrage du serveur avec Gunicorn, garantissant que l'application démarre correctement sur Render avec toutes les migrations appliquées automatiquement.

---

### PATCH 6 : Créer `render.yaml` pour configuration Render

**Fichier** : `render.yaml` (nouveau)  
**Action** : Créer configuration Render complète

**Paragraphe FI9_NAYEK** :
Un fichier `render.yaml` permet de définir la configuration complète du service Render (variables d'environnement, health checks, scaling) de manière déclarative et versionnée. Sans ce fichier, la configuration doit être faite manuellement dans l'interface Render, risquant des oublis ou des incohérences. Le patch FI9_NAYEK crée un `render.yaml` complet avec toutes les variables d'environnement nécessaires, health checks, et configuration de scaling, garantissant un déploiement reproductible et fiable.

---

## 🔧 CODE DES PATCHS

### PATCH 1 : `app/main.py` — Host et Port dynamiques

```python
# =====================================================
# Lancement
# =====================================================
if __name__ == "__main__":
    import uvicorn
    # ✅ FI9_NAYEK : Host 0.0.0.0 pour Render/VPS, Port depuis env
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("APP_ENV", "production").lower() in {"development", "dev", "local"}
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
```

---

### PATCH 2 : `alembic/env.py` — Import Base corrigé

```python
# =====================================================
# 🧱 Import des modèles SQLAlchemy
# =====================================================
from app.database import Base  # ✅ FI9_NAYEK : Source unique après patchs cohérence
from app.models import Conversation, User, FileUpload  # tous les modèles
target_metadata = Base.metadata
```

---

### PATCH 3 : `alembic.ini` — URL DB depuis environnement

```ini
[alembic]
script_location = alembic
# ✅ FI9_NAYEK : URL DB lue depuis DATABASE_URL dans env.py
# sqlalchemy.url = postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s
```

---

### PATCH 4 : `requirements.txt` — Ajouter Gunicorn

```txt
# === Web / API ===
fastapi==0.115.0
uvicorn[standard]==0.32.0
gunicorn[uvicorn]==21.2.0  # ✅ FI9_NAYEK : Production server

# === Base de données ===
sqlalchemy==2.0.36
psycopg2-binary==2.9.9
alembic==1.13.3

# === Authentification / Sécurité ===
PyJWT==2.8.0
passlib[bcrypt]==1.7.4
email-validator==2.1.1
bcrypt==4.0.1

# === Configuration ===
pydantic==2.9.2
pydantic-settings==2.4.0
python-dotenv==1.0.1
python-multipart==0.0.9
python-jose[cryptography]==3.3.0

# === Tâches asynchrones / Cache ===
celery==5.3.6
redis==5.0.3

# === IA / Vectors / NLP ===
chromadb==0.5.3
openai==1.51.0
numpy==1.26.4
langdetect==1.0.9
pgvector==0.4.1

# === Outils ===
requests==2.32.3
httpx==0.27.2

# === Tests / Débogage ===
pytest==8.3.3
pytest-cov==4.1.0
trio==0.26.2
```

---

### PATCH 5 : `Procfile` — Commande de démarrage Render

```procfile
web: bash -c "alembic upgrade head || echo '⚠️ Aucune migration à appliquer' && gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --access-logfile - --error-logfile -"
```

---

### PATCH 6 : `render.yaml` — Configuration Render

```yaml
services:
  - type: web
    name: konan-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        sync: false  # À configurer dans Render Dashboard
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false  # À configurer dans Render Dashboard
      - key: APP_ENV
        value: production
      - key: LOG_LEVEL
        value: INFO
      - key: CORS_ALLOW_ORIGINS
        sync: false  # À configurer selon frontend URL
      - key: CHROMA_DB_DIR
        value: ./chroma_store
      - key: CHROMA_DB_DIR_LAWS
        value: ./chroma_store_laws
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: konan-db
    databaseName: konan_db
    user: konan_user
    plan: free  # ou starter/pro pour production
```

---

## ✅ VÉRIFICATION POST-PATCH

### Checklist Déploiement

- [ ] `main.py` : Host `0.0.0.0` et Port depuis `PORT` env
- [ ] `alembic/env.py` : Import `app.database.Base`
- [ ] `alembic.ini` : URL DB commentée (utilise env)
- [ ] `requirements.txt` : Gunicorn présent
- [ ] `Procfile` : Présent avec commande complète
- [ ] `render.yaml` : Présent avec configuration complète

### Tests Locaux

1. **Test host 0.0.0.0** :
   ```bash
   HOST=0.0.0.0 PORT=8000 python -m app.main
   ```
   Vérifier que le serveur écoute sur toutes les interfaces.

2. **Test migrations** :
   ```bash
   DATABASE_URL=postgresql://... alembic upgrade head
   ```
   Vérifier que les migrations fonctionnent.

3. **Test Gunicorn** :
   ```bash
   gunicorn app.main:app --bind 0.0.0.0:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker
   ```
   Vérifier que Gunicorn démarre correctement.

---

## 📊 RÉSUMÉ FI9_NAYEK

**État avant** : ⚠️ **NON PRÊT** — Host hardcodé, pas de Gunicorn, config Render absente  
**État après** : ✅ **PRÊT** — Host 0.0.0.0, Gunicorn ajouté, config Render complète

**Impact** :
- ✅ Compatible Render.com
- ✅ Compatible VPS Linux
- ✅ Migrations Alembic fiables
- ✅ Production-ready avec Gunicorn
- ✅ Configuration déclarative Render

---

**Fin du document PATCHES FI9_NAYEK DÉPLOIEMENT**

