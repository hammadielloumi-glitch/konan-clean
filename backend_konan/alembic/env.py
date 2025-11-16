import os
import sys
import socket
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# =====================================================
# 📦 Chargement de l'environnement et du chemin projet
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

# =====================================================
# ⚙️ Configuration Alembic
# =====================================================
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =====================================================
# 🔧 Détection automatique de l’URL de base de données
# =====================================================
def detect_database_url():
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 🔍 Détection du service Docker ou local
    try:
        socket.gethostbyname("konan_db")
        return "postgresql+psycopg2://postgres:pass123@konan_db:5432/konan_db"
    except socket.error:
        return "postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db"

DATABASE_URL = detect_database_url()
print(f"DATABASE_URL detectee : {DATABASE_URL}")

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# =====================================================
# 🧱 Import des modèles SQLAlchemy
# =====================================================
from app.database import Base  # ✅ FI9_NAYEK : Source unique après patchs cohérence
from app.models import Conversation, User, FileUpload  # tous les modèles
target_metadata = Base.metadata

# =====================================================
# 🚀 Exécution des migrations Alembic
# =====================================================
def run_migrations_online():
    """Exécute les migrations Alembic en ligne."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
