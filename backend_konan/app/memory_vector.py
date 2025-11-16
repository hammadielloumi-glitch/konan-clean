# ============================================
# app/memory_vector.py — Version stable (Konan Master PRO)
# ============================================

import os
import traceback
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
from app.vector.chroma_manager import chroma_client

# ======================================================
# 🔧 CHARGEMENT .env
# ======================================================
# Chargement explicite du fichier d'environnement avant toute initialisation OpenAI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(ENV_PATH)

# Vérification de la clé
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY introuvable — vérifie ton fichier .env ou son encodage UTF-8 sans BOM")

# ======================================================
# 🔧 INITIALISATION
# ======================================================
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

try:
    client_openai = OpenAI(api_key=api_key)
    print("OpenAI initialise avec succes dans memory_vector.py")
except Exception as e:
    print(f"Erreur lors de l'initialisation OpenAI : {e}")
    client_openai = None

# ======================================================
# 💾 ENREGISTREMENT MÉMOIRE VECTORIELLE
# ======================================================
def store_memory(session_id: str, message_user: str, message_konan: str):
    """Enregistre les échanges dans la mémoire vectorielle (ChromaDB)."""
    try:
        collection = chroma_client.get_or_create_collection("konan_memory")
        document_text = f"USER: {message_user}\nKONAN: {message_konan}"
        collection.add(documents=[document_text], ids=[f"{session_id}_{abs(hash(message_user))}"])
        total_items = len(collection.get().get("ids", []))
        print(f"[MEMOIRE SAUVEGARDEE] session={session_id} | total={total_items}")
    except Exception as e:
        print(f"[ERREUR ENREGISTREMENT MEMOIRE] {e}")
        if client_openai:
            try:
                client_openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=f"USER: {message_user}\nKONAN: {message_konan}"
                )
                print("[MEMOIRE VIA OPENAI] Sauvegarde alternative OK")
            except Exception as ee:
                print(f"[ERREUR MEMOIRE VECTORIELLE FINALE] {ee}")

# ======================================================
# 🔍 RECHERCHE CONTEXTE VECTORIEL
# ======================================================
def retrieve_similar_context(query: str, n_results: int = 3):
    """Recherche les conversations similaires à la requête actuelle."""
    try:
        collection = chroma_client.get_or_create_collection("konan_memory")
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        print(f"[CONTEXTE RETROUVE] {len(docs)} resultat(s)")
        return docs
    except Exception as e:
        print(f"[ERREUR RECHERCHE CONTEXTE] {e}")
        if client_openai:
            try:
                client_openai.embeddings.create(model="text-embedding-3-small", input=query)
                print("[CONTEXTE VIA OPENAI] Embedding fallback OK")
                return []
            except Exception as ee:
                print(f"[ERREUR CONTEXTE VECTORIEL FINALE] {ee}")
        return []

# ======================================================
# 🧩 ROUTES FASTAPI — CHROMA INSPECTION
# ======================================================
router = APIRouter(prefix="/api/memory", tags=["Memory Vectorielle"])

@router.get("/inspect")
def inspect_memory():
    try:
        collection = chroma_client.get_or_create_collection("konan_memory")
        data = collection.get()
        ids = data.get("ids", [])
        docs = data.get("documents", [])
        total = len(ids)
        print(f"[INSPECT] {total} elements trouves dans la memoire.")
        return {
            "total": total,
            "samples": [{"id": ids[i], "text": docs[i][:600]} for i in range(min(5, total))],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d’inspection mémoire : {e}")

@router.get("/stats")
def memory_stats():
    try:
        collection = chroma_client.get_or_create_collection("konan_memory")
        data = collection.get()
        total = len(data.get("ids", []))
        docs = data.get("documents", [])
        size_kb = sum(len(doc.encode("utf-8")) for doc in docs) / 1024
        return {
            "status": "ok",
            "total_items": total,
            "approx_size_kb": round(size_kb, 2),
            "message": "📊 Statistiques mémoire vectorielle OK",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques : {e}")

@router.delete("/clear")
def clear_memory():
    try:
        chroma_client.reset()
        print("Memoire vectorielle effacee avec succes.")
        return {"status": "ok", "message": "Mémoire vectorielle supprimée avec succès ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage : {e}")

@router.get("/ping")
def ping_memory():
    try:
        test_collection = chroma_client.get_or_create_collection("ping_check")
        if test_collection is None:
            raise HTTPException(status_code=500, detail="❌ ChromaDB non disponible.")
        return {"status": "ok", "message": "✅ ChromaDB répond — en ligne", "store_path": CHROMA_DIR}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ping mémoire : {e}")
