from fetch import fetch_items
from embed import build_embed
from score import calculate_score
from utils import load_user_list
from seen_manager import load_seen_ids, save_seen_ids
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


# --- 設定読み込み -----------------------------------------------------------

PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)
EXCLUDE_USERS = load_user_list(EXCLUDE_USERS_PATH)


# --- タイトル決定（通常通知用） --------------------------------------------

def determine_title(top_label):
    if top_label == "🔥特選":
        return "📢SKIMA　新着通知"
    if top_label == "✨おすすめ":
        return "🔔SKIMA　新着通知"
    return "📝SKIMA　新着通知"


def safe_top_label(embed):
    for f in embed.get("fields", []):
        if f["name"] == "優先度":
            return f["value"]
    return ""


# --- メイン処理 -------------------------------------------------------------

def main():
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    seen = load_seen_ids()
    items = fetch_items()

    new_items = []

    # --- フィルタリング -----------------------------------------------------

    for item in items:

        if item["id"] in seen:
            continue

        if item["author_id"] in EXCLUDE_USERS:
            continue

        if item["price"] >= 15000:
            continue

        item["score"] = calculate_score(item["price"])
        new_items.append(item)

    # --- 新規なし -----------------------------------------------------------

    if not new_items:
        print("新規なし")
        seen.update(item["id"] for item in items)
        save_seen_ids(seen)
        return

    # --- 優先 / 通常 に分割 -------------------------------------------------

    priority_items = [i for i in new_items if i["author_id"] in PRIORITY_USERS]
    normal_items   = [i for i in new_items if i["author_id"] not in PRIORITY_USERS]

    # --- 優先通知（深夜帯でも送る） ----------------------------------------

    if priority_items:
        priority_items.sort(key=lambda x: -x["score"])

        embeds = []
        for item in priority_items[:10]:
            embed = build_embed(item)
            embed["color"] = 0xFFD700  # 金色
            embeds.append(embed)

        # 前のピンを解除
        last = load_last_pin()
        if last:
            unpin_message(last["id"])

        # 新しい優先通知を送信（@everyone 付き）
        msg = send_bot_message("@everyone\n💌SKIMA 優先通知", embeds)

        # ピン止め
        if "id" in msg:
            pin_message(msg["id"])
            save_last_pin(msg["id"])

    # --- 通常通知（深夜帯はスキップ） --------------------------------------

    if 1 <= now.hour < 6:
        print("深夜帯のため通常通知はスキップ")
    else:
        if normal_items:
            normal_items.sort(key=lambda x: -x["score"])
            embeds = [build_embed(item) for item in normal_items[:10]]

            top_label = safe_top_label(embeds[0])
            title = determine_title(top_label)

            # ★ 通常通知は @everyone を付けない
            send_webhook_message(title, embeds)

    # --- seen.json 更新 ------------------------------------------------------

    seen.update(item["id"] for item in items)
    save_seen_ids(seen)


# --- 実行 -------------------------------------------------------------------

if __name__ == "__main__":
    main()
