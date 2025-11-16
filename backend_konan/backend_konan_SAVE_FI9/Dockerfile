# ==========================================
# KONAN BACKEND — FastAPI + Alembic + Uvicorn (version finale validée)
# ==========================================
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Variables d'environnement globales
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    CHROMA_DB_DIR=./chroma_store \
    CHROMA_DB_DIR_LAWS=./chroma_store_laws \
    CHROMA_TELEMETRY_DISABLED=true \
    PATH="/usr/local/bin:$PATH"

# Dépendances système (PostgreSQL + build + Rust pour ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel --root-user-action=ignore \
    && pip install --no-cache-dir -r requirements.txt --root-user-action=ignore
RUN pip install --no-cache-dir reportlab
# Copie du code source complet
COPY . .

# Création des répertoires persistants
RUN mkdir -p /app/chroma_store /app/chroma_store_laws

# Port exposé
EXPOSE 8000

# Commande de démarrage
CMD ["bash", "-c", "\
    echo '🔧 Initialisation du backend Konan'; \
    alembic upgrade head || echo '⚠️ Aucune migration à appliquer'; \
    echo '🚀 Lancement du serveur FastAPI'; \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 \
"]
