from fetch import fetch_items
from embed import build_embed
from score import calculate_score
from utils import load_user_list
from seen_manager import load_seen_ids, save_seen_ids
from notify import send_combined_notification
from config.settings import PRIORITY_USERS_PATH, EXCLUDE_USERS_PATH

PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)
EXCLUDE_USERS = load_user_list(EXCLUDE_USERS_PATH)

def determine_title(has_priority, top_label):
    if has_priority:
        return "@everyone\n💌SKIMA　優先通知"

    if top_label == "🔥特選":
        return "📢SKIMA　新着通知"
    elif top_label == "✨おすすめ":
        return "🔔SKIMA　新着通知"
    else:
        return "📝SKIMA　新着通知"

def safe_top_label(embed):
    fields = embed.get("fields", [])
    for f in fields:
        if f["name"] == "優先度":
            return f["value"]
    return ""

def main():
    seen = load_seen_ids()
    items = fetch_items()

    new_items = []
    for item in items:
        if item["id"] in seen:
            continue
        if item["author_id"] in EXCLUDE_USERS:
            continue

        item["score"] = calculate_score(item["price"])
        new_items.append(item)

    if not new_items:
        print("新規なし")
        return

    new_items.sort(key=lambda x: (
        x["author_id"] not in PRIORITY_USERS,
        -x["score"]
    ))

    embeds = [build_embed(item) for item in new_items[:10]]

    # 🔥 特選 or ✨おすすめ or 優先ユーザー → @everyone
    has_priority = any(
        item["author_id"] in PRIORITY_USERS or item["score"] >= 2
        for item in new_items
    )

    top_label = safe_top_label(embeds[0])
    title = determine_title(has_priority, top_label)

    send_combined_notification(title, embeds)

    seen.update(item["id"] for item in new_items)
    save_seen_ids(seen)

if __name__ == "__main__":
    main()
