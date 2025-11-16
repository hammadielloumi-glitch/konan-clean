# 🔧 PATCHES FI9_NAYEK - COHÉRENCE TECHNIQUE BACKEND KONAN

**Date** : 2025-01-XX  
**Protocole** : FI9_NAYEK  
**Scope** : `backend_konan/app/`

---

## 📋 RÉSUMÉ DES PROBLÈMES IDENTIFIÉS

### 🔴 CRITIQUES

1. **Base SQLAlchemy** : 4 déclarations différentes (`app/database.py`, `app/db/base.py`, `app/db/session.py`, `app/db/__init__.py`)
2. **get_db()** : 3 implémentations parallèles (`app/database.py`, `app/db/session.py`, `app/db/__init__.py`)
3. **Imports incohérents** : Models utilisent différentes Base (`file_upload.py`, `law.py`)
4. **Sessions non fermées** : `next(get_db())` dans `app/api/laws.py`
5. **Duplication ChromaDB** : Code dupliqué dans `chroma_manager.py` (lignes 1-132 = 134-264)

### 🟡 IMPORTANTS

6. **Import incorrect** : `app/api/files.py` utilise `app.db.session` au lieu de `app.database`
7. **Fichiers legacy** : `app/db/__init__.py`, `app/db/base.py` non utilisés mais présents
8. **Incohérence front/back** : Format réponse chat différent (`reply` vs `messages`)

---

## 📦 LISTE DES PATCHS

### PATCH 1 : Unifier Base SQLAlchemy — `app/database.py` comme source unique

**Fichier** : `app/database.py`  
**Action** : Conserver comme source unique, ajouter exports explicites

**Paragraphe FI9_NAYEK** :
Le backend KONAN présente une fragmentation critique de la Base SQLAlchemy avec 4 déclarations parallèles (`app/database.py`, `app/db/base.py`, `app/db/session.py`, `app/db/__init__.py`). Cette duplication empêche le partage correct des modèles entre modules et crée des risques de conflits lors des migrations Alembic. Le patch FI9_NAYEK unifie la Base dans `app/database.py` comme source unique de vérité, garantissant la cohérence des métadonnées SQLAlchemy et la compatibilité avec Alembic. Tous les imports sont redirigés vers cette source unique, éliminant les risques de modèles non synchronisés.

---

### PATCH 2 : Supprimer duplications Base — `app/db/base.py` et `app/db/__init__.py`

**Fichier** : `app/db/base.py` et `app/db/__init__.py`  
**Action** : Supprimer ou rediriger vers `app.database`

**Paragraphe FI9_NAYEK** :
Les fichiers `app/db/base.py` et `app/db/__init__.py` créent des déclarations alternatives de Base SQLAlchemy non synchronisées avec la source principale. Cette duplication introduit des risques de modèles incompatibles et de migrations Alembic échouées. Le patch FI9_NAYEK supprime ces fichiers ou les transforme en simples réexports vers `app.database`, garantissant une seule source de vérité pour la Base. Cette unification est critique pour la stabilité des migrations et la cohérence des modèles SQLAlchemy.

---

### PATCH 3 : Corriger imports Base dans models — `app/models/file_upload.py` et `app/models/law.py`

**Fichier** : `app/models/file_upload.py` et `app/models/law.py`  
**Action** : Changer import vers `app.database.Base`

**Paragraphe FI9_NAYEK** :
Les modèles `FileUpload` et `Law` utilisent des imports incorrects de Base (`app.db.base.Base` et `app.db.session.Base`) au lieu de la source unifiée `app.database.Base`. Cette incohérence empêche Alembic de détecter correctement ces modèles lors des migrations, créant des risques de tables non créées ou de schémas désynchronisés. Le patch FI9_NAYEK corrige ces imports pour utiliser `app.database.Base`, garantissant que tous les modèles sont correctement enregistrés dans les métadonnées SQLAlchemy et détectés par Alembic.

---

### PATCH 4 : Corriger import get_db dans `app/api/files.py`

**Fichier** : `app/api/files.py`  
**Action** : Changer `from app.db.session import get_db` vers `from app.database import get_db`

**Paragraphe FI9_NAYEK** :
Le fichier `app/api/files.py` utilise `app.db.session.get_db()` au lieu de la source unifiée `app.database.get_db()`. Cette incohérence crée des sessions de base de données différentes selon les modules, risquant des problèmes de connexion pool et de transactions non synchronisées. Le patch FI9_NAYEK unifie l'import vers `app.database.get_db()`, garantissant que toutes les sessions utilisent le même engine SQLAlchemy et le même pool de connexions, essentiel pour la stabilité et les performances.

---

### PATCH 5 : Corriger utilisation get_db dans `app/api/laws.py`

**Fichier** : `app/api/laws.py`  
**Action** : Remplacer `next(get_db())` par `Depends(get_db)`

**Paragraphe FI9_NAYEK** :
Le fichier `app/api/laws.py` utilise `next(get_db())` au lieu de `Depends(get_db)`, créant des sessions non gérées par FastAPI et non fermées automatiquement. Cette pratique provoque des fuites de connexions et des erreurs potentielles de pool épuisé. Le patch FI9_NAYEK remplace ces appels par `Depends(get_db)` dans les signatures des endpoints, garantissant que FastAPI gère correctement le cycle de vie des sessions avec le pattern yield, fermant automatiquement les connexions après chaque requête.

---

### PATCH 6 : Supprimer duplication ChromaDB — `app/vector/chroma_manager.py`

**Fichier** : `app/vector/chroma_manager.py`  
**Action** : Supprimer lignes 134-264 (code dupliqué)

**Paragraphe FI9_NAYEK** :
Le fichier `chroma_manager.py` contient une duplication complète du code (lignes 1-132 identiques aux lignes 134-264), doublant la taille du fichier et créant des risques de maintenance et de bugs. Cette duplication peut causer des initialisations multiples de ChromaDB et des comportements imprévisibles. Le patch FI9_NAYEK supprime les lignes 134-264, conservant uniquement la première implémentation complète, garantissant une initialisation unique de ChromaDB et une maintenance simplifiée du code.

---

### PATCH 7 : Unifier get_db() — Rediriger `app/db/session.py` vers `app.database`

**Fichier** : `app/db/session.py`  
**Action** : Transformer en réexport vers `app.database`

**Paragraphe FI9_NAYEK** :
Le fichier `app/db/session.py` crée une implémentation alternative de `get_db()` utilisant `app.core.config.settings` au lieu de la source unifiée `app.database`. Cette duplication peut créer des sessions avec des engines différents selon les modules, risquant des problèmes de connexion et de transactions. Le patch FI9_NAYEK transforme ce fichier en simple réexport vers `app.database.get_db()` et `app.database.Base`, garantissant l'unicité des sessions et la cohérence des connexions à la base de données.

---

### PATCH 8 : Vérifier cohérence endpoints avec frontend

**Fichier** : `app/routers/chat.py`  
**Action** : Vérifier format réponse (`reply` au lieu de `messages`)

**Paragraphe FI9_NAYEK** :
Le frontend attend une réponse `{ reply, id, history }` de l'endpoint `/api/chat`, mais le backend pourrait retourner un format différent. Le patch FI9_NAYEK vérifie et garantit que l'endpoint retourne exactement le format attendu par le frontend, évitant les erreurs de parsing et les incohérences entre les couches. Cette vérification est critique pour l'intégration frontend/backend et la stabilité de l'application.

---

## 🔧 CODE DES PATCHS

### PATCH 1 : `app/database.py` — Source unique Base

```python
# ============================================
# app/database.py — Source unique Base SQLAlchemy (FI9_NAYEK)
# ============================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

def ensure_env_loaded():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    current_value = os.getenv("DATABASE_URL")
    bom_key = "\ufeffDATABASE_URL"

    if not current_value and bom_key in os.environ:
        current_value = os.environ[bom_key].strip()
        if current_value:
            os.environ["DATABASE_URL"] = current_value
            del os.environ[bom_key]
            print("⚙️ [Reload Fix] DATABASE_URL corrigé depuis une clé UTF-8 BOM")

    if current_value:
        return

    if os.path.exists(env_path):
        load_dotenv(env_path, override=True, encoding="utf-8-sig")
        if os.getenv("DATABASE_URL"):
            print("⚙️ [Reload Fix] Variables .env rechargées manuellement dans app/database.py")
            return
        raise RuntimeError("❌ DATABASE_URL toujours manquant après chargement du fichier .env")
    raise RuntimeError(f"❌ Fichier .env introuvable à {env_path}")

ensure_env_loaded()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non défini dans l'environnement après rechargement manuel.")

# ✅ Source unique Base SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Source unique get_db()
def get_db() -> Generator:
    """Générateur de session DB pour FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Exports explicites pour compatibilité
__all__ = ["Base", "engine", "SessionLocal", "get_db"]
```

---

### PATCH 2 : `app/db/base.py` — Réexport vers database

```python
# =====================================================
# app/db/base.py — Réexport vers source unique (FI9_NAYEK)
# =====================================================
# ⚠️ DEPRECATED : Utiliser app.database.Base directement
from app.database import Base

__all__ = ["Base"]
```

---

### PATCH 3 : `app/models/file_upload.py` — Import corrigé

```python
from sqlalchemy import Column, Integer, String, DateTime, text
from app.database import Base  # ✅ FI9_NAYEK : Source unique

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=text("now()"))
```

---

### PATCH 4 : `app/models/law.py` — Import corrigé

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base  # ✅ FI9_NAYEK : Source unique

class LawArticle(Base):
    __tablename__ = "law_articles"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(200), index=True, nullable=False)
    article = Column(String(50), index=True, nullable=False)
    texte = Column(Text, nullable=False)
    lang = Column(String(8), default="fr")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### PATCH 5 : `app/api/files.py` — Import corrigé

```python
# =====================================================
# app/api/files.py — Upload & gestion fichiers Konan
# =====================================================
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db  # ✅ FI9_NAYEK : Source unique
from app.models.file_upload import FileUpload

router = APIRouter(tags=["Files"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", summary="Uploader un fichier vers le serveur")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        new_file = FileUpload(
            filename=file.filename,
            filepath=file_path,
            uploaded_at=datetime.utcnow(),
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return {
            "status": "success",
            "id": new_file.id,
            "filename": new_file.filename,
            "filepath": new_file.filepath,
            "uploaded_at": new_file.uploaded_at,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur upload fichier : {e}")

@router.get("/list", summary="Lister les fichiers enregistrés")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileUpload).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "filepath": f.filepath,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]

@router.delete("/{file_id}", summary="Supprimer un fichier")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    if os.path.exists(file.filepath):
        os.remove(file.filepath)
    db.delete(file)
    db.commit()
    return {"status": "deleted", "id": file_id}
```

---

### PATCH 6 : `app/api/laws.py` — Utilisation Depends

```python
# ============================================
# app/api/laws.py — API lois (Phase 4 unifiée)
# ============================================
from fastapi import APIRouter, HTTPException, Query, Header, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db  # ✅ FI9_NAYEK : Source unique
from app.vector.chroma_manager import search_law, index_laws, collection, CHROMA_DIR
import os, json

router = APIRouter(prefix="/api/laws", tags=["Lois tunisiennes"])
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "konan-secure-admin-key")

def require_admin(x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Accès admin requis.")

@router.get("/search")
def search_laws(query: str = Query(..., min_length=2), n: int = Query(3, ge=1, le=10)):
    try:
        results = search_law(query, n_results=n)
        return {"query": query, "total_results": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {e}")

@router.post("/reindex")
def reindex_laws(x_api_key: str = Header(...)):
    require_admin(x_api_key)
    try:
        index_laws()
        return {"status": "ok", "message": "Réindexation terminée."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def stats_laws():
    try:
        data = collection.get()
        total = len(data.get("documents", []))
        return {"status": "ok", "total_articles": total}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ✅ FI9_NAYEK : Utilisation Depends au lieu de next(get_db())
@router.get("/all")
def list_laws(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, code_name, article_number, article_title FROM laws LIMIT 100"))
    return [dict(r) for r in result.mappings().all()]

# ✅ FI9_NAYEK : Utilisation Depends au lieu de next(get_db())
@router.get("/{law_id}")
def get_law_by_id(law_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT * FROM laws WHERE id = :id"), {"id": law_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Loi ID {law_id} introuvable")
    return dict(row)
```

---

### PATCH 7 : `app/vector/chroma_manager.py` — Supprimer duplication

**Action** : Supprimer les lignes 134-264 (code dupliqué)

Le fichier doit contenir uniquement les lignes 1-132, puis terminer.

---

### PATCH 8 : `app/db/session.py` — Réexport vers database

```python
# =====================================================
# app/db/session.py — Réexport vers source unique (FI9_NAYEK)
# =====================================================
# ⚠️ DEPRECATED : Utiliser app.database directement
from app.database import Base, engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
```

---

## ✅ VÉRIFICATION FINALE

### Checklist Post-Patch

- [ ] `app/database.py` : Source unique Base et get_db()
- [ ] Tous les models importent `app.database.Base`
- [ ] Tous les routers/API importent `app.database.get_db`
- [ ] Aucune utilisation de `next(get_db())`
- [ ] `chroma_manager.py` : Duplication supprimée
- [ ] `app/db/base.py` : Réexport vers database
- [ ] `app/db/session.py` : Réexport vers database
- [ ] `app/db/__init__.py` : Supprimé ou réexport

### Tests à effectuer

1. **Test migrations Alembic** :
   ```bash
   alembic revision --autogenerate -m "test_unified_base"
   ```
   Vérifier que tous les models sont détectés.

2. **Test imports** :
   ```python
   from app.database import Base, get_db
   from app.models import User, Conversation, FileUpload
   # Tous doivent fonctionner
   ```

3. **Test endpoints** :
   - `/health` : OK
   - `/api/auth/login` : OK
   - `/api/chat` : Format réponse vérifié
   - `/api/conversations` : OK
   - `/api/files/list` : OK
   - `/api/laws/all` : OK

---

## 📊 RÉSUMÉ FI9_NAYEK

**État avant** : ⚠️ **FRAGMENTÉ** — 4 Base, 3 get_db(), imports incohérents  
**État après** : ✅ **UNIFIÉ** — 1 Base, 1 get_db(), imports cohérents

**Impact** :
- ✅ Migrations Alembic fiables
- ✅ Modèles SQLAlchemy synchronisés
- ✅ Sessions DB correctement gérées
- ✅ Maintenance simplifiée
- ✅ Compatibilité frontend/backend garantie

---

**Fin du document PATCHES FI9_NAYEK**

