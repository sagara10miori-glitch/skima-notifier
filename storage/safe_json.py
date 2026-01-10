import json
import os

STORAGE_PATH = "storage/seen.json"

def load_seen_ids():
    if not os.path.exists(STORAGE_PATH):
        return []

    try:
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_seen_ids(ids):
    os.makedirs("storage", exist_ok=True)

    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)
