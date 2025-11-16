#!/usr/bin/env python3
"""
Indexer complet des lois tunisiennes dans PostgreSQL + pgvector (production).
Compatible avec ton corpus laws_tn.json
"""

import os, sys, json, gzip, time, argparse, logging
from datetime import datetime
from typing import Iterable, Dict, Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    OpenAI = None

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "laws_index.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("laws_index")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--file", "-f", default=None)
    p.add_argument("--batch", "-b", type=int, default=500)
    p.add_argument("--model", "-m", default="text-embedding-3-large")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--language", default="fr")
    return p.parse_args()

# -------------------- Lecture corpus --------------------
def autodetect_corpus_path() -> str:
    for c in [
        os.path.join(BASE_DIR, "scripts", "data", "laws_tn.json.gz"),
        os.path.join(BASE_DIR, "scripts", "data", "laws_tn.json"),
    ]:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError("Aucun corpus trouvé")

def iter_corpus(path: str):
    open_fn = gzip.open if path.endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8") as f:
        first = f.read(1)
        f.seek(0)
        if first == "[":
            for row in json.load(f):
                yield row
        else:
            for line in f:
                if line.strip():
                    yield json.loads(line)

# -------------------- PostgreSQL --------------------
def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL manquant")
        sys.exit(2)
    return create_engine(url, pool_pre_ping=True)

def ensure_pgvector(eng: Engine):
    with eng.begin() as c:
        c.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

def ensure_indexes(eng: Engine):
    with eng.begin() as c:
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_laws_text_search ON laws USING GIN (to_tsvector('french', article_text));"))
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_laws_vector ON laws USING ivfflat (vector_embedding vector_cosine_ops);"))

# -------------------- Embeddings --------------------
def build_openai_client():
    if not OPENAI_AVAILABLE:
        return None
    key = os.getenv("OPENAI_API_KEY")
    if not key or not key.startswith("sk-"):
        return None
    return OpenAI(api_key=key)

def fake_embed_batch(texts: List[str], dim: int = 1536) -> List[List[float]]:
    out = []
    for t in texts:
        acc = sum(ord(c) for c in (t[:128] or "")) % 997
        out.append([((acc + i) % 997) / 997.0 for i in range(dim)])
    return out

# -------------------- Normalisation --------------------
def normalize_row(row: Dict[str, Any], lang: str) -> Dict[str, Any]:
    return {
        "code_name": (row.get("code_name") or row.get("code") or "").strip(),
        "article_number": (row.get("article_number") or "").strip(),
        "article_title": (row.get("article_title") or "").strip(),
        "article_text": (row.get("article_text") or row.get("content") or "").strip(),
        "chapter": row.get("chapter"),
        "keywords": row.get("keywords"),
        "category": row.get("category"),
        "date_entry": row.get("date_entry"),
        "source_url": row.get("source_url"),
        "language": row.get("language") or lang,
    }

# -------------------- Insertion --------------------
def insert_batch(eng: Engine, rows: List[Dict[str, Any]], embeds: List[List[float]]):
    if not rows:
        return
    with eng.begin() as c:
        for i, r in enumerate(rows):
            c.execute(
                text("""
                INSERT INTO laws
                (code_name, article_number, article_title, article_text, chapter,
                 keywords, category, date_entry, source_url, last_update, language, vector_embedding)
                VALUES (:code_name, :article_number, :article_title, :article_text, :chapter,
                        :keywords, :category, :date_entry, :source_url, NOW(), :language, :vector_embedding)
                ON CONFLICT (code_name, article_number)
                DO UPDATE SET
                    article_text = EXCLUDED.article_text,
                    article_title = EXCLUDED.article_title,
                    vector_embedding = EXCLUDED.vector_embedding,
                    last_update = NOW();
                """),
                {**r, "vector_embedding": embeds[i]},
            )

# -------------------- Main --------------------
def main():
    args = parse_args()
    path = args.file or autodetect_corpus_path()
    print(f"📦 Corpus: {path}")
    print(f"🔗 DB: {os.getenv('DATABASE_URL')}")
    eng = get_engine()
    ensure_pgvector(eng)
    ensure_indexes(eng)
    client = build_openai_client()
    use_fake = client is None
    if use_fake:
        print("Embeddings simules (offline).")
    total = 0
    start = time.time()
    buffer = []
    for raw in iter_corpus(path):
        row = normalize_row(raw, args.language)
        if not row["code_name"] or not row["article_number"] or not row["article_text"]:
            continue
        buffer.append(row)
        if len(buffer) >= args.batch:
            texts = [r["article_text"] for r in buffer]
            embeds = fake_embed_batch(texts) if use_fake else client.embeddings.create(model=args.model, input=texts).data
            if not use_fake:
                embeds = [d.embedding for d in embeds]
            insert_batch(eng, buffer, embeds)
            total += len(buffer)
            print(f"... {total} articles traites")
            buffer.clear()
    if buffer:
        texts = [r["article_text"] for r in buffer]
        embeds = fake_embed_batch(texts) if use_fake else [d.embedding for d in client.embeddings.create(model=args.model, input=texts).data]
        insert_batch(eng, buffer, embeds)
        total += len(buffer)
    print(f"Termine: {total} articles indexes en {time.time()-start:.1f}s")
    with eng.begin() as c:
        r = c.execute(text("SELECT COUNT(*) FROM laws")).scalar()
        print(f"📊 Total en base: {r}")

if __name__ == "__main__":
    main()
