from fetch import fetch_items
from embed import build_embed
from score import calculate_score
from utils import load_user_list
from seen_manager import load_seen_ids, save_seen_ids
from notify import send_combined_notification
from config.settings import PRIORITY_USERS_PATH, EXCLUDE_USERS_PATH
from datetime import datetime
import pytz

# --- 深夜帯スキップ ---------------------------------------------------------

jst = pytz.timezone("Asia/Tokyo")
now = datetime.now(jst)

if 1 <= now.hour < 6:
    print("深夜帯（1:00〜6:00）のため通知をスキップ")
    exit()

# --- 設定読み込み -----------------------------------------------------------

PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)
EXCLUDE_USERS = load_user_list(EXCLUDE_USERS_PATH)

# --- タイトル決定 -----------------------------------------------------------

def determine_title(has_priority, top_label):
    if has_priority:
        return "@everyone\n💌SKIMA　優先通知"
    if top_label == "🔥特選":
        return "@everyone\n📢SKIMA　新着通知"
    if top_label == "✨おすすめ":
        return "@everyone\n🔔SKIMA　新着通知"
    return "📝SKIMA　新着通知"

def safe_top_label(embed):
    for f in embed.get("fields", []):
        if f["name"] == "優先度":
            return f["value"]
    return ""

# --- メイン処理 -------------------------------------------------------------

def main():
    seen = load_seen_ids()
    items = fetch_items()

    # --- フィルタリング -----------------------------------------------------

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

    # --- 新規なし -----------------------------------------------------------

    if not new_items:
        print("新規なし")
        seen.update(item["id"] for item in items)
        save_seen_ids(seen)
        return

    # --- 並び替え（優先ユーザー → スコア高い順） --------------------------

    new_items.sort(key=lambda x: (
        x["author_id"] not in PRIORITY_USERS,
        -x["score"]
    ))

    embeds = [build_embed(item) for item in new_items[:10]]

    # --- 通知タイトル --------------------------------------------------------

    has_priority = any(item["author_id"] in PRIORITY_USERS for item in new_items)
    top_label = safe_top_label(embeds[0])
    title = determine_title(has_priority, top_label)

    # --- 通知送信 -----------------------------------------------------------

    send_combined_notification(title, embeds)

    # --- seen.json 更新 ------------------------------------------------------

    seen.update(item["id"] for item in items)
    save_seen_ids(seen)

# --- 実行 -------------------------------------------------------------------

if __name__ == "__main__":
    main()
