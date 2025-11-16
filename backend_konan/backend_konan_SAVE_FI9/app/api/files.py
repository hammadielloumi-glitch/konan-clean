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

# Dossier de stockage local (assure-toi qu’il existe)
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================
# 📤 Upload d’un fichier
# =====================================================
@router.post("/upload", summary="Uploader un fichier vers le serveur")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Sauvegarde du fichier sur disque
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Enregistrement en base
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

# =====================================================
# 📄 Liste des fichiers
# =====================================================
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

# =====================================================
# 🗑️ Suppression d’un fichier
# =====================================================
@router.delete("/{file_id}", summary="Supprimer un fichier")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    # Suppression physique si présent
    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    db.delete(file)
    db.commit()

    return {"status": "deleted", "id": file_id}
