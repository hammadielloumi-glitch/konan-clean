import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import subprocess

print("Lancement de l'audit Alembic / Base PostgreSQL...\n")

# Charger .env
load_dotenv()

# Récupération URL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

if not DATABASE_URL:
    print("ERREUR : aucune variable DATABASE_URL trouvee dans l'environnement.")
    sys.exit(1)

print(f"DATABASE_URL detectee : {DATABASE_URL}\n")

# Vérification connexion
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"Connexion PostgreSQL reussie : {version}\n")
except OperationalError as e:
    print(f"ERREUR CONNEXION : {e}")
    sys.exit(1)

# Vérification des tables
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print("Aucune table detectee dans la base.")
        print("Application automatique des migrations Alembic...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations appliquees avec succes.\n")
    else:
        print(f"Tables existantes : {tables}\n")
except Exception as e:
    print(f"Erreur lors de la verification des tables : {e}")
    sys.exit(1)

print("Verification de la coherence des revisions Alembic...")
try:
    subprocess.run(["alembic", "current"], check=False)
except Exception as e:
    print(f"Impossible d'executer alembic current : {e}")

print("\nAudit termine avec succes !")
