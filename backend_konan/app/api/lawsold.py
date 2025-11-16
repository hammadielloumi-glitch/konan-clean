# ============================================
# app/api/laws.py — API juridique tunisienne (officielle + logs + notifications Pro)
# ============================================
import os
import shutil
import smtplib
import requests
import json
import difflib
from datetime import datetime
from email.mime.text import MIMEText
from fastapi import APIRouter, Query, HTTPException, Header
from app.vector.chroma_manager import search_law, index_laws, collection, CHROMA_DIR
from sqlalchemy.orm import Session
from app.models.law_diff_log import LawDiffLog
from app.database import SessionLocal


router = APIRouter(prefix="/api", tags=["Lois tunisiennes"])

# ======================================================
# 🔐 CLÉ D’AUTORISATION ADMIN KONAN
# ======================================================
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "konan-secure-admin-key")

def require_admin(x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="⛔ Accès réservé à l’Admin API Konan.")

# ======================================================
# 🧾 LOGGING STRUCTURÉ + ALERTES MAIL
# ======================================================
LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "updates.log")
os.makedirs(LOG_DIR, exist_ok=True)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@konan.pro")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "konan.system@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "password-placeholder")

def log_update(action: str, source: str, validator: str, status: str):
    entry = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "action": action,
        "source": source,
        "validator": validator,
        "status": status
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    try:
        send_mail_notification(entry)
    except Exception as e:
        print(f"[ERREUR MAIL] {e}")

def send_mail_notification(entry: dict):
    """Envoie une notification e-mail à l’administrateur."""
    subject = f"[KONAN LEGAL UPDATE] {entry['action']} - {entry['status']}"
    body = (
        f"🕒 {entry['timestamp']}\n"
        f"Action : {entry['action']}\n"
        f"Source : {entry['source']}\n"
        f"Validé par : {entry['validator']}\n"
        f"Résultat : {entry['status']}\n\n"
        f"📘 Journal : {LOG_FILE}"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
        print(f"Mail envoye a {ADMIN_EMAIL}")

# ======================================================
# 🔍 Recherche vectorielle
# ======================================================
@router.get("/search_law")
def search_law_api(query: str = Query(...), n: int = Query(2, ge=1, le=10)):
    results = search_law(query, n_results=n)
    return {"query": query, "total_results": len(results), "results": results}

# ======================================================
# ⚙️ Réindexation manuelle
# ======================================================
@router.post("/index_laws")
def index_laws_api(x_api_key: str = Header(...)):
    require_admin(x_api_key)
    try:
        index_laws()
        log_update("Réindexation", "interne", "Admin API Konan", "succès")
        return {"status": "ok", "message": "✅ Réindexation terminée avec succès."}
    except Exception as e:
        log_update("Réindexation", "interne", "Admin API Konan", f"erreur: {e}")
        return {"status": "error", "message": str(e)}

# ======================================================
# 🧹 Réinitialisation totale du store
# ======================================================
@router.delete("/reset_laws")
def reset_laws_api(x_api_key: str = Header(...)):
    require_admin(x_api_key)
    try:
        if os.path.exists(CHROMA_DIR):
            shutil.rmtree(CHROMA_DIR)
            os.makedirs(CHROMA_DIR, exist_ok=True)
            log_update("Reset", CHROMA_DIR, "Admin API Konan", "succès")
            return {"status": "ok", "message": f"🧹 Store ChromaDB réinitialisé : {CHROMA_DIR}"}
        return {"status": "ok", "message": f"Aucun store trouvé à {CHROMA_DIR}"}
    except Exception as e:
        log_update("Reset", CHROMA_DIR, "Admin API Konan", f"erreur: {e}")
        return {"status": "error", "message": str(e)}

# ======================================================
# 📊 Statistiques globales
# ======================================================
@router.get("/stats_laws")
def stats_laws_api():
    try:
        data = collection.get()
        docs = data.get("documents", [])
        metas = data.get("metadatas", [])
        total = len(docs)
        codes = list({m.get("code", "inconnu") for m in metas})

        size_mb = sum(
            os.path.getsize(os.path.join(root, f))
            for root, _, files in os.walk(CHROMA_DIR)
            for f in files
        ) / (1024 * 1024)

        return {
            "status": "ok",
            "total_articles": total,
            "codes_detected": codes,
            "store_path": CHROMA_DIR,
            "store_size_MB": round(size_mb, 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ======================================================
# 🔔 NOTIFICATIONS UTILISATEURS PRO
# ======================================================
NOTIFY_FILE = "/app/app/data/notifications.json"
os.makedirs(os.path.dirname(NOTIFY_FILE), exist_ok=True)

def add_notification(title: str, content: str, source: str):
    """Ajoute une notification lisible par les utilisateurs Pro."""
    notif = {
        "id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "title": title,
        "content": content,
        "source": source,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "new"
    }

    try:
        data = []
        if os.path.exists(NOTIFY_FILE):
            with open(NOTIFY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data.insert(0, notif)
        with open(NOTIFY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Notification enregistree pour les utilisateurs Pro : {title}")
    except Exception as e:
        print(f"[ERREUR NOTIFICATION] {e}")

@router.get("/notifications")
def get_notifications():
    """Retourne la liste des notifications disponibles pour les utilisateurs Pro."""
    try:
        if os.path.exists(NOTIFY_FILE):
            with open(NOTIFY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"total": len(data), "notifications": data}
        return {"total": 0, "notifications": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# ✅ Marquer les notifications comme lues
# ======================================================
@router.post("/notifications/mark_as_read")
def mark_notifications_as_read():
    """Marque toutes les notifications comme lues."""
    try:
        if not os.path.exists(NOTIFY_FILE):
            return {"status": "ok", "message": "Aucune notification à mettre à jour."}

        with open(NOTIFY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for notif in data:
            notif["status"] = "read"

        with open(NOTIFY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("Toutes les notifications marquees comme lues.")
        return {"status": "ok", "message": "Toutes les notifications ont été marquées comme lues."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# 🌐 Chargement et validation des mises à jour officielles
# ======================================================
@router.post("/load_laws_from_url")
def load_laws_from_url(
    url: str = Query(...),
    x_api_key: str = Header(...)
):
    require_admin(x_api_key)

    allowed_domains = ["justice.gov.tn", "legislation.tn"]
    if not any(domain in url for domain in allowed_domains):
        raise HTTPException(status_code=400, detail="❌ Source non officielle ou non autorisée.")

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Erreur HTTP {response.status_code} lors du chargement.")
        content = response.text

        save_path = "/app/app/data/updates/"
        os.makedirs(save_path, exist_ok=True)
        file_name = os.path.basename(url).replace("/", "_") + ".html"
        full_path = os.path.join(save_path, file_name)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        log_update("Import officiel", url, "Admin API Konan", "succès")

        # 🔔 Notification automatique utilisateurs Pro
        add_notification(
            title="Nouvelle mise à jour juridique",
            content=f"Mise à jour officielle importée depuis {url}. Les lois sont maintenant à jour.",
            source=url
        )

        return {
            "status": "ok",
            "message": "📥 Mise à jour légale téléchargée, archivée et notifiée.",
            "source_url": url,
            "saved_file": full_path,
            "log_file": LOG_FILE
        }

    except Exception as e:
        log_update("Import officiel", url, "Admin API Konan", f"erreur: {e}")
        return {"status": "error", "message": str(e)}
        # 🔔 Notification automatique utilisateurs Pro
        add_notification(
            title="Nouvelle mise à jour juridique",
            content=f"Mise à jour officielle importée depuis {url}. Les lois sont maintenant à jour.",
            source=url
        )

        # 🚀 Diffusion en temps réel (Pro Premium)
        from app.api.laws_ws import broadcast_notification
        import asyncio
        asyncio.create_task(broadcast_notification({
            "title": "Nouvelle mise à jour juridique",
            "content": f"Import officiel depuis {url}",
            "source": url,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }))
# ======================================================
# ⚖️ Comparaison entre deux versions d'une loi
# ======================================================


@router.post("/laws/compare_version")
def compare_law_versions(
    old_text: str = Query(..., description="Ancienne version de la loi"),
    new_text: str = Query(..., description="Nouvelle version de la loi"),
    validator: str = Query("Admin API Konan")
):
    """
    Compare deux versions d’un texte juridique et retourne les différences.
    Génère un log et une notification si un changement significatif est détecté.
    """

    try:
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        diff = difflib.ndiff(old_lines, new_lines)
        added, removed, unchanged = [], [], []

        for line in diff:
            if line.startswith("+ "):
                added.append(line[2:])
            elif line.startswith("- "):
                removed.append(line[2:])
            elif line.startswith("  "):
                unchanged.append(line[2:])

        result = {
            "summary": {
                "added": len(added),
                "removed": len(removed),
                "unchanged": len(unchanged),
            },
            "details": {
                "added_text": added,
                "removed_text": removed,
                "unchanged_sample": unchanged[:5],
            }
        }

                # 🔐 Journalisation automatique
        status = "modifications détectées" if added or removed else "aucune différence"
        log_update("Comparaison versions", "interne", validator, status)

        # 🔔 Notification utilisateurs Pro si changement
        if added or removed:
            add_notification(
                title="Changement détecté dans un texte juridique",
                content=f"{len(added)} ajouts et {len(removed)} suppressions détectés dans la nouvelle version.",
                source="Comparateur de lois"
            )

        # ✅ Sauvegarde du diff dans la base
        try:
            db: Session = SessionLocal()
            diff_entry = LawDiffLog(
                source="interne",
                validator=validator,
                added=len(added),
                removed=len(removed),
                timestamp=datetime.utcnow()
            )
            db.add(diff_entry)
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

        return {"status": "ok", "result": result}

    except Exception as e:
        log_update("Comparaison versions", "interne", validator, f"erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))
