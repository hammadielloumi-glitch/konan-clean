# app/core/chroma_client.py
import chromadb
from chromadb.config import Settings
import os

PERSIST_DIR = os.path.join("app", "vector", "chroma_data")

def get_collection(name: str = "laws"):
    os.makedirs(PERSIST_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    return client.get_or_create_collection(name)
