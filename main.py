import datetime
import pytz
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
    PRIORITY_USERS_FILE,
    EXCLUDE_USERS_FILE,
    PRICE_LIMIT,
)

import json


# ---------------------------------------------------------
# 設定読み込み
# ---------------------------------------------------------
with open(PRIORITY_USERS_FILE, "r", encoding="utf-8") as f:
    PRIORITY_USERS = set(json.load(f))

with open(EXCLUDE_USERS_FILE, "r", encoding="utf-8") as f:
    EXCLUDE_USERS = set(json.load(f))


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

        new_items.append(item)

    print(f"[INFO] new_items = {len(new_items)}")

    # ---------------------------------------------------------
    # 優先 / 通常 に分類
    # ---------------------------------------------------------
    priority_items = [
        item for item in new_items if item["author_id"] in PRIORITY_USERS
    ]
    normal_items = [
        item for item in new_items if item["author_id"] not in PRIORITY_USERS
    ]

    print(f"[INFO] priority_items = {len(priority_items)}")
    print(f"[INFO] normal_items = {len(normal_items)}")

    # ---------------------------------------------------------
    # 通知処理
    # ---------------------------------------------------------
    # 優先通知（Bot）
    for item in priority_items:
        embeds = [build_embed(item)]
        result = send_bot_message("@everyone", embeds)
        print(f"[INFO] priority send result: {result}")

        # ピン固定
        if "id" in result:
            last_pin = load_last_pin()
            if last_pin:
                unpin_message(last_pin["id"])
            pin_message(result["id"])
            save_last_pin(result["id"])

        seen.add(item["id"])

    # 通常通知（Webhook）
    for item in normal_items:
        embeds = [build_embed(item)]
        result = send_webhook_message("", embeds)
        print(f"[INFO] normal send result: {result}")
        seen.add(item["id"])

    # ---------------------------------------------------------
    # 古い既読データの削除
    # ---------------------------------------------------------
    deleted = seen.cleanup_old_entries(days=7)
    print(f"[INFO] cleanup_old_entries: deleted={deleted}")


if __name__ == "__main__":
    main()
