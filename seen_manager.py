import json

def load_seen_ids():
    try:
        with open("seen.json", "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen_ids(seen):
    # 半年以上前の ID を削除（肥大化防止）
    if len(seen) > 50000:
        seen = set(list(seen)[-30000:])

    with open("seen.json", "w") as f:
        json.dump(list(seen), f)
