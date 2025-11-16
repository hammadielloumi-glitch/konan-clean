# =====================================================
# app/main.py — Correction FI9_NAYEK : persistance de .env sous Windows
# =====================================================

import os
from dotenv import load_dotenv

# Chargement initial du .env avant tout import interne
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, "..", ".env")
load_dotenv(env_path, override=not os.getenv("DATABASE_URL"), encoding="utf-8-sig")

# =====================================================
# 📦 IMPORTS INTERNES APRÈS LE CHARGEMENT DU .env
# =====================================================
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json, logging
from .webhooks.sync_user import router as supabase_user_sync_router
from .api.auth import router as auth_router
from app.database import get_db, engine
from app.models import Conversation
from app.schemas import ChatRequest
from app.memory_vector import store_memory, router as memory_vector_router
from app.api import files, laws, auth_seed
from app.api.routes import conversations
from app.routers import stripe_router
from app.routers.chat import router as chat_router

# =====================================================
# ⚙️ CONFIGURATION ENVIRONNEMENT
# =====================================================
db_url = os.getenv("DATABASE_URL")
openai_key = os.getenv("OPENAI_API_KEY")
TEST_MODE = os.getenv("KONAN_TEST_MODE", "0") == "1"
APP_ENV = os.getenv("APP_ENV", "production")

if TEST_MODE:
    print("MODE TEST : AUTH BYPASS ACTIVÉ")
    if APP_ENV.lower() not in {"development", "dev", "local"}:
        logging.warning("MODE TEST activé alors que APP_ENV=%s — vérifier la configuration.", APP_ENV)

# =====================================================
# 🧾 JOURNALISATION STRUCTURÉE
# =====================================================
LOG_DIR = os.path.join(base_dir, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "konan_chat.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s", encoding="utf-8")

def log_json(event: dict):
    event["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

# =====================================================
# 🚀 APPLICATION FASTAPI
# =====================================================
from openai import OpenAI
client: OpenAI | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    if TEST_MODE or not openai_key or openai_key.startswith("sk-fake"):
        print("Mode test activé - OpenAI désactivé")
        client = None
    else:
        try:
            client = OpenAI(api_key=openai_key)
            print("OpenAI activé - GPT-4o-mini prêt")
        except Exception as e:
            print(f"Erreur OpenAI init : {e}")
            client = None
    yield

app = FastAPI(
    title="Konan API ⚖️",
    version="1.8",
    description="Backend IA juridique tunisien — Auth réelle + Stripe simulation",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =====================================================
# 🌐 CONFIGURATION CORS
# =====================================================
origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
def parse_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

ALLOW_ORIGINS = parse_origins(origins_env)
if not ALLOW_ORIGINS:
    fallback = ["http://localhost:5173", "exp://127.0.0.1:19000"]
    ALLOW_ORIGINS = fallback if TEST_MODE else ["https://app.konan.tld"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# =====================================================
# 🔗 ROUTERS
# =====================================================
# =====================================================
# 🔗 ROUTERS - Mode C Supabase Auth
# =====================================================
# FI9_NAYEK v12.1 : Router Mode C Supabase Auth
# - app/api/auth.py : Router Mode C avec prefix="/api/auth"
# - Endpoint /api/auth/me utilise get_current_user() Mode C
# - Messages d'erreur standardises FI9-401, FI9-403, etc.
# auth_router a déjà son propre prefix="/api/auth" défini dans app/api/auth.py
app.include_router(auth_router)  # Router Mode C - PRIORITAIRE
print("[FI9] Supabase Mode C Auth actif")
app.include_router(auth_seed.router, prefix="/api/auth", tags=["Auth"])
app.include_router(memory_vector_router, prefix="/api/memory", tags=["Memory"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(laws.router, prefix="/api/laws", tags=["Laws"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(stripe_router.router, prefix="/api/stripe", tags=["Stripe"])
# Webhook Supabase pour synchronisation utilisateur (Mode C)
app.include_router(supabase_user_sync_router)
# =====================================================
# 🩺 HEALTH CHECKS
# =====================================================
@app.get("/")
def root():
    """Route racine - redirige vers /health pour vérification"""
    return {
        "status": "ok",
        "message": "Konan API opérationnelle",
        "version": "1.8",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "Konan API opérationnelle"}

@app.get("/test_db")
def test_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()")).fetchone()
    return {"status": "DB OK", "timestamp": str(result[0])}

# =====================================================
# 🧩 PATCH WINDOWS : persistance des variables dans le reloader
# =====================================================
if os.name == "nt" and not os.getenv("DATABASE_URL"):
    load_dotenv(env_path)
    print("⚙️ Variables rechargées manuellement dans le reloader (Windows).")

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

