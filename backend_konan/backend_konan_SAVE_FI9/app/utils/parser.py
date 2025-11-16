import json

def iter_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: 
                continue
            yield json.loads(line)
