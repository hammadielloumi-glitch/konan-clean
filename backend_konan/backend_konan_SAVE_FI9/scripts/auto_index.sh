#!/usr/bin/env bash
export PYTHONPATH="$(dirname "$0")/.."
python - <<'PY'
from app.vector.index_laws import index_dir
print(index_dir("app/data/corpus","laws"))
PY
