"""
Place-holder sans réseau: interface unifiée.
Implémente deux modes:
- 'file://'  : lit un fichier local et le renvoie (pour tests offline)
- 'noop'     : ne fait rien, renvoie []
"""
from pathlib import Path
from .parser import iter_jsonl

def fetch_to_jsonl(source_url: str, out_path: str) -> int:
    if source_url.startswith("file://"):
        p = Path(source_url.replace("file://",""))
        if not p.exists():
            return 0
        # copie directe "fichier déjà JSONL"
        Path(out_path).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        return sum(1 for _ in iter_jsonl(out_path))
    # autres modes à brancher ultérieurement (scraping JORT/API)
    Path(out_path).write_text("", encoding="utf-8")
    return 0
