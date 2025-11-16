"""
Tâche périodique: récupérer sources → (optionnel) générer JSONL → indexer.
Branchée par cron ou appel admin.
"""
from app.utils.jort_scraper import fetch_to_jsonl
from app.vector.index_laws import index_dir

def run_update(sources: list[str] | None = None, out_dir: str = "app/data/corpus") -> dict:
    # sources ex: ["file://app/data/corpus/code_commerce.jsonl", ...]
    if sources:
        for s in sources:
            name = s.split("/")[-1]
            out_path = f"{out_dir}/{name}"
            fetch_to_jsonl(s, out_path)
    return index_dir(out_dir, "laws")
