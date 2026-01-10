# seen_manager.py

import json

def load_seen_ids():
    try:
        with open("seen.json", "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen_ids(ids):
    ids = sorted(set(ids))[-500:]

    with open("seen.json", "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)
