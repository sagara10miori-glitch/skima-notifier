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
        # すでに取得済みなら通知しない
        if item["id"] in seen:
            continue

        # 除外ユーザー
        if item["author_id"] in EXCLUDE_USERS:
            continue

        # スコア付与
        item["score"] = calculate_score(item["price"])
        new_items.append(item)

    if not new_items:
        print("新規なし")
        # ★ 今回取得した全アイテムを seen に追加（通知なしでも記録）
        seen.update(item["id"] for item in items)
        save_seen_ids(seen)
        return

    # 並び順：優先ユーザー → スコア高い順
    new_items.sort(key=lambda x: (
        x["author_id"] not in PRIORITY_USERS,
        -x["score"]
    ))

    embeds = [build_embed(item) for item in new_items[:10]]

    # ★ 優先ユーザー or 特選 or おすすめ が含まれる場合は @everyone
    has_priority = any(
        item["author_id"] in PRIORITY_USERS or item["score"] >= 2
        for item in new_items
    )

    top_label = safe_top_label(embeds[0])
    title = determine_title(has_priority, top_label)

    send_combined_notification(title, embeds)

    # ★ 今回取得した全アイテムを seen に追加（通知したものだけでなく全部）
    seen.update(item["id"] for item in items)
    save_seen_ids(seen)

if __name__ == "__main__":
    main()
