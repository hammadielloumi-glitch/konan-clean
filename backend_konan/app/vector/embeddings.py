import os
from typing import List
import hashlib

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

def _hash_embed(text: str, dim: int = 1536) -> List[float]:
    # fallback déterministe offline pour tests (non sémantique)
    h = hashlib.sha256(text.encode("utf-8")).digest()
    base = list(h)*((dim // len(h))+1)
    return [b/255.0 for b in base[:dim]]

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not OPENAI_API_KEY:
        return [_hash_embed(t) for t in texts]
    # OpenAI client minimal sans dépendance externe
    import requests, json
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"}
    data = {"input": texts, "model": MODEL}
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
    r.raise_for_status()
    js = r.json()
    return [d["embedding"] for d in js["data"]]
