#!/usr/bin/env python3
# scripts/import_laws_exhaustive.py
import os, sys, json
from typing import Iterable
from chromadb import Client
from chromadb.config import Settings

CHROMA_DIR = os.getenv("CHROMA_DB_DIR_LAWS", "./chroma_store_laws")
COLLECTION = os.getenv("LAWS_COLLECTION", "laws_tunisia")

def iter_jsonl(paths: Iterable[str]):
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Importer des lois tunisiennes au format JSONL")
    ap.add_argument("--paths", nargs="+", required=True, help="Fichiers .jsonl à importer")
    ap.add_argument("--batch", type=int, default=512, help="Taille de lot")
    args = ap.parse_args()

    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = Client(Settings(persist_directory=CHROMA_DIR, anonymized_telemetry=True))
    col = client.get_or_create_collection(COLLECTION)

    docs, ids, metas = [], [], []
    total = 0
    for i, rec in enumerate(iter_jsonl(args.paths)):
        doc = f"{rec.get('article_title','')} — {rec.get('content','')}"
        meta = {
            "code": rec.get("code",""),
            "article": rec.get("article_title",""),
            "law_number": rec.get("law_number",""),
            "jort_ref": rec.get("jort_ref",""),
            "last_update": rec.get("last_update","")
        }
        docs.append(doc)
        ids.append(f"{meta['code']}_{meta['article']}_{i}")
        metas.append(meta)

        if len(docs) >= args.batch:
            col.add(documents=docs, ids=ids, metadatas=metas)
            total += len(docs)
            print(f"[+] Importé: {total}")
            docs, ids, metas = [], [], []

    if docs:
        col.add(documents=docs, ids=ids, metadatas=metas)
        total += len(docs)
        print(f"[+] Importé: {total}")

    print(f"Import termine. Total: {total} documents -> {COLLECTION} in {CHROMA_DIR}")

if __name__ == "__main__":
    sys.exit(main())
