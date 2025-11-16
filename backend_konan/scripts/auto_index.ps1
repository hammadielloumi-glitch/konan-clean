python - << 'PY'
from app.core.chroma_client import get_collection
c = get_collection("laws")
print("✅ total documents :", len(c.get()['ids']))
PY