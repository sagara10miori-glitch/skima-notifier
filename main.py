from fetch import fetch_items
from embed import build_embed
from score import calculate_score
from utils import load_user_list
from seen_manager import load_seen_ids, mark_seen, cleanup_old_entries
from notify import (
    send_webhook_message,
    send_bot_message,
    pin_message,
    unpin_message,
    load_last_pin,
    save_last_pin
)
from config.settings import PRIORITY_USERS_PATH, EXCLUDE_USERS_PATH
from datetime import datetime
from zoneinfo import ZoneInfo


PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)
EXCLUDE_USERS = load_user_list(EXCLUDE_USERS_PATH)


def determine_title(top_label):
    if top_label == "🔥特選":
        return "📢SKIMA 新着通知"
    if top_label == "✨おすすめ":
        return "🔔SKIMA 新着通知"
    return "📝SKIMA 新着通知"


def safe_top_label(item):
    return item.get("rank", "")


def main():
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    is_night = 1 <= now.hour < 6

    seen = load_seen_ids()

    items = fetch_items(priority_only=is_night) or []
    print(f"[INFO] fetched {len(items)} items (night={is_night})")

    new_items = []

    for item in items:
        if item["id"] in seen:
            continue
        if item["author_id"] in EXCLUDE_USERS:
            continue
        if item["price"] >= 15000:
            continue

        item["score"] = calculate_score(item["price"])
        new_items.append(item)

    print(f"[INFO] new_items = {len(new_items)}")

    if not new_items:
        cleanup_old_entries()
        return

    priority_items = [i for i in new_items if i.get("author_id") in PRIORITY_USERS]
    normal_items = [i for i in new_items if i.get("author_id") not in PRIORITY_USERS]

    print(f"[INFO] priority_items = {len(priority_items)}")
    print(f"[INFO] normal_items = {len(normal_items)}")

    # --- 優先通知（@everyone 付き） ---
    if priority_items:
        priority_items.sort(key=lambda x: -x["score"])
        embeds = [build_embed(item, is_priority=True) for item in priority_items[:10]]

        last = load_last_pin()
        if last and "id" in last:
            unpin_message(last["id"])

        msg = send_bot_message("@everyone\n💌SKIMA 優先通知", embeds)

        if isinstance(msg, dict) and "id" in msg:
            pin_message(msg["id"])
            save_last_pin(msg["id"])

    # --- 通常通知（@everyone なし） ---
    if not is_night and normal_items:
        normal_items.sort(key=lambda x: -x["score"])
        embeds = [build_embed(item) for item in normal_items[:10]]

        top_label = safe_top_label(normal_items[0])
        title = determine_title(top_label)

        send_webhook_message(title, embeds)

    for item in new_items:
        mark_seen(item["id"])

    cleanup_old_entries()


if __name__ == "__main__":
    main()
