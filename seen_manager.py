import json
import time

SEEN_FILE = "seen.json"
KEEP_DAYS = 7
KEEP_SECONDS = KEEP_DAYS * 24 * 60 * 60


def load_seen_ids():
    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)  # {id: timestamp}
    except:
        return {}


def save_seen_ids(seen_dict):
    now = time.time()

    # 1週間より古いIDを削除
    cleaned = {
        item_id: ts
        for item_id, ts in seen_dict.items()
        if now - ts <= KEEP_SECONDS
    }

    with open(SEEN_FILE, "w") as f:
        json.dump(cleaned, f)


def mark_seen(seen_dict, item_id):
    seen_dict[item_id] = time.time()
