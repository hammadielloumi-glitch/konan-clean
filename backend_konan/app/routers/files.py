from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models import FileUpload  # table que tu as utilisée pour stocker les fichiers
from app.database import get_db
from app.core.security import verify_jwt
import os

router = APIRouter(prefix="/api/files", tags=["files"], dependencies=[Depends(verify_jwt)])

@router.get("/{file_id}")
def get_uploaded_file(file_id: str, db: Session = Depends(get_db), user=Depends(verify_jwt)):
    """Renvoie le fichier uploadé par son ID"""
    file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    if not os.path.exists(file.path):
        raise HTTPException(status_code=410, detail="Fichier supprimé du disque")

    return FileResponse(
        path=file.path,
        filename=file.name,
        media_type=file.mime_type or "application/octet-stream"
    )
