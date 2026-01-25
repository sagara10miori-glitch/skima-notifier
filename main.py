import datetime
import pytz
import json

from fetch import fetch_items
from embed import build_embed
from notify import (
    send_webhook_message,
    send_bot_message,
    load_last_pin,
    save_last_pin,
    unpin_message,
    pin_message,
)
from seen_manager import SeenManager
from config.settings import (
    PRIORITY_USERS_PATH,
    EXCLUDE_USERS_PATH,
    PRICE_LIMIT,
)

# ---------------------------------------------------------
# TXT 読み込み
# ---------------------------------------------------------
with open(PRIORITY_USERS_PATH, "r", encoding="utf-8") as f:
    PRIORITY_USERS = {line.strip() for line in f if line.strip()}

with open(EXCLUDE_USERS_PATH, "r", encoding="utf-8") as f:
    EXCLUDE_USERS = {line.strip() for line in f if line.strip()}


# ---------------------------------------------------------
# 優先度の数値化
# ---------------------------------------------------------
def priority_value(prefix):
    if prefix.startswith("💌"):
        return 1
    if prefix.startswith("🔥"):
        return 2
    if prefix.startswith("⭐"):
        return 3
    if prefix.startswith("✨"):
        return 4
    return 5


# ---------------------------------------------------------
# 絵文字だけ返す
# ---------------------------------------------------------
def prefix_emoji(prefix):
    if prefix.startswith("💌"):
        return "💌"
    if prefix.startswith("🔥"):
        return "🔥"
    if prefix.startswith("⭐"):
        return "⭐"
    if prefix.startswith("✨"):
        return "✨"
    return "🔔"


# ---------------------------------------------------------
# @everyone は 💌 のときだけ
# ---------------------------------------------------------
def needs_everyone(prefixes):
    return any(p.startswith("💌") for p in prefixes)


# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
def main():
    # 現在時刻（JST）
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(jst)
    night = 1 <= now.hour <= 5

    print(f"[INFO] run at {now.isoformat()} (night={night})")

    # 既読管理
    seen = SeenManager("seen.db")
    print(f"[INFO] seen_ids = {seen.count()}")

    # 深夜帯は優先ユーザーのみ取得
    items = fetch_items(priority_only=night)
    print(f"[INFO] fetched = {len(items)}")

    new_items = []
    for item in items:
        if not item["id"]:
            continue

        if item["author_id"] in EXCLUDE_USERS:
            continue

        if item["price"] >= PRICE_LIMIT:
            continue

        if seen.exists(item["id"]):
            continue

        # 優先ユーザー情報を embed に渡すために付与
        item["is_priority"] = item["author_id"] in PRIORITY_USERS

        new_items.append(item)

    print(f"[INFO] new_items = {len(new_items)}")

    # ---------------------------------------------------------
    # embed生成（prefixも受け取る）
    # ---------------------------------------------------------
    embeds = []
    prefixes = []
    ids = []

    for item in new_items:
        embed, prefix = build_embed(item)
        embeds.append(embed)
        prefixes.append(prefix)
        ids.append(item["id"])

    if not embeds:
        print("[INFO] no new embeds")
        return

    # ---------------------------------------------------------
    # 優先度順に並べ替え
    # ---------------------------------------------------------
    sorted_data = sorted(
        zip(embeds, prefixes, ids),
        key=lambda x: priority_value(x[1])
    )

    embeds = [e for e, p, i in sorted_data]
    prefixes = [p for e, p, i in sorted_data]
    ids = [i for e, p, i in sorted_data]

    # ---------------------------------------------------------
    # 見出しの決定（絵文字のみ）
    # ---------------------------------------------------------
    top_prefix = prefixes[0] if prefixes else ""
    emoji = prefix_emoji(top_prefix)

    header_text = f"{emoji} SKIMA新着通知"

    # @everyone は 💌 のときだけ
    content = "@everyone " + header_text if needs_everyone(prefixes) else header_text

    # ---------------------------------------------------------
    # 1メッセージで送信（Webhook）
    # ---------------------------------------------------------
    result = send_webhook_message(content, embeds)
    print(f"[INFO] send result: {result}")

    # ピン固定（最優先の1件のみ）
    if "id" in result:
        last_pin = load_last_pin()
        if last_pin:
            unpin_message(last_pin["id"])
        pin_message(result["id"])
        save_last_pin(result["id"])

    # 既読登録
    for item_id in ids:
        seen.add(item_id)

    # ---------------------------------------------------------
    # 古い既読データの削除
    # ---------------------------------------------------------
    deleted = seen.cleanup_old_entries(days=7)
    print(f"[INFO] cleanup_old_entries: deleted={deleted}")


if __name__ == "__main__":
    main()
