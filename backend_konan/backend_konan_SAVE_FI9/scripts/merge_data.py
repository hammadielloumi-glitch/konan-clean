# backend_konan/scripts/merge_data.py
import json, glob, os

SRC_DIR = os.path.join(os.path.dirname(__file__), "../app/data")
DST = os.path.join(os.path.dirname(__file__), "data/laws_tn.json")

os.makedirs(os.path.dirname(DST), exist_ok=True)

with open(DST, "w", encoding="utf-8") as out:
    for file in glob.glob(os.path.join(SRC_DIR, "*.json")):
        if file.endswith(".bak") or "schema" in file:
            continue
        print(f"📚 Lecture : {os.path.basename(file)}")
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Fusion terminee -> {DST}")
