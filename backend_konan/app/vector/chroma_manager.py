# ============================================
# app/vector/chroma_manager.py — Base juridique tunisienne (persistante stable)
# ============================================
import os
import json
import chromadb
from chromadb.config import Settings
from difflib import get_close_matches
import re
import shutil

# ------------------------------------------------------
# 🧩 INITIALISATION UNIQUE ET PERSISTANTE DE CHROMADB
# ------------------------------------------------------
CHROMA_DIR = os.getenv("CHROMA_DB_DIR_LAWS", "/app/chroma_store_laws")
os.makedirs(CHROMA_DIR, exist_ok=True)

if not hasattr(chromadb, "_shared_client"):
    chromadb._shared_client = chromadb.Client(
        Settings(
            persist_directory=CHROMA_DIR,
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
    )

chroma_client = chromadb._shared_client
collection = chroma_client.get_or_create_collection("laws_tunisia")
print(f"ChromaDB initialise (persistant) dans {CHROMA_DIR}")

# ======================================================
# 🧩 VÉRIFICATION ET CORRECTION DES JSON
# ======================================================
def verify_json_integrity(base_dir="/app/app/data"):
    """
    Vérifie et corrige automatiquement les fichiers JSON mal formatés.
    Crée une copie de sauvegarde .bak avant toute modification.
    """
    for file in os.listdir(base_dir):
        if not file.endswith(".json"):
            continue
        path = os.path.join(base_dir, file)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()

            # Sauvegarde avant correction
            shutil.copy(path, f"{path}.bak")

            # Si ce n’est pas une liste JSON valide, on corrige automatiquement
            if not content.startswith("["):
                content = re.sub(r"}\s*{", "},{", content)
                content = f"[{content}]"
                data = json.loads(content)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Corrige automatiquement : {file} ({len(data)} articles)")
            else:
                json.load(open(path, encoding="utf-8"))
                print(f"JSON valide : {file}")

        except Exception as e:
            print(f"[JSON invalide] {file} - {e}")

# ======================================================
# 📥 INDEXATION DES TEXTES DE LOIS
# ======================================================
def load_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def index_laws():
    base_dir = "/app/app/data"
    verify_json_integrity(base_dir)  # Vérifie et corrige les JSON avant indexation
    files = ["penal.json", "csp.json", "loi_58.json"]
    total = 0

    for file in files:
        path = os.path.join(base_dir, file)
        if not os.path.exists(path):
            print(f"[Fichier manquant] {file}")
            continue

        data = load_json(path)
        for i, art in enumerate(data):
            # Normalisation des clés pour éviter les KeyError
            art_norm = {k.lower(): v for k, v in art.items()}
            article = art_norm.get("article", art_norm.get("titre", f"article_{i}"))
            content = art_norm.get("content", art_norm.get("texte", ""))
            code = art_norm.get("code", "")

            if not content:
                print(f"[Article ignore] {article} (vide ou invalide)")
                continue

            text = f"{article} — {content}"
            collection.add(
                documents=[text],
                ids=[f"{file}_{i}"],
                metadatas=[{"code": code, "article": article}]
            )
            total += 1

    print(f"Indexation terminee ({total} articles)")

# ======================================================
# 🔍 RECHERCHE VECTORIELLE + FALLBACK TEXTUEL
# ======================================================
def search_law(query: str, n_results: int = 2):
    """
    Recherche vectorielle + fallback textuel si aucun résultat direct.
    """
    try:
        print(f"[Requete recue] {query}")
        results = collection.query(query_texts=[query.lower()], n_results=n_results)
        docs = results.get("documents", [[]])[0]

        if not docs:
            # 🔁 fallback textuel approximatif
            all_docs = collection.get().get("documents", [])
            matches = get_close_matches(query.lower(), [d.lower() for d in all_docs], n=1, cutoff=0.2)
            if matches:
                i = [d.lower() for d in all_docs].index(matches[0])
                return [all_docs[i]]
            return ["Aucun article pertinent trouvé."]

        return docs

    except Exception as e:
        print(f"[ERREUR SEARCH LAW] {e}")
        return ["Erreur lors de la recherche de loi."]
