import re

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def strip_headers(text: str) -> str:
    # retire numéros/entêtes parasites au début de lignes
    return re.sub(r"^\s*(Article\s+\d+\s*:?)", r"\1 ", text, flags=re.IGNORECASE|re.MULTILINE)

def clean_record(rec: dict) -> dict:
    rec["source"] = normalize_whitespace(rec.get("source",""))
    rec["article"] = normalize_whitespace(rec.get("article",""))
    rec["texte"] = normalize_whitespace(strip_headers(rec.get("texte","")))
    rec["lang"] = rec.get("lang","fr")
    return rec
