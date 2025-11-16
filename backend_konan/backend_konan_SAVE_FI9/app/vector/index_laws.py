from pathlib import Path
from app.utils.parser import iter_jsonl
from app.utils.cleaner import clean_record
from app.vector.embeddings import embed_texts
from app.core.chroma_client import get_collection  # suppose présent dans chroma_client.py

def index_file(jsonl_path: str, collection_name: str = "laws"):
    col = get_collection(collection_name)
    ids, docs, metas = [], [], []
    for rec in iter_jsonl(jsonl_path):
        rec = clean_record(rec)
        _id = f"{rec['source']}::{rec['article']}"
        ids.append(_id)
        docs.append(rec["texte"])
        metas.append({"source": rec["source"], "article": rec["article"], "lang": rec["lang"]})
    if not docs:
        return 0
    embs = embed_texts(docs)
    col.add(ids=ids, embeddings=embs, documents=docs, metadatas=metas)
    return len(docs)

def index_dir(dir_path: str = "app/data/corpus", collection_name: str = "laws") -> dict:
    p = Path(dir_path)
    stats = {}
    for f in sorted(p.glob("*.jsonl")):
        n = index_file(str(f), collection_name)
        stats[f.name] = n
    return stats
