# main.py

import json
import os
from fetch import fetch_items
from embed import build_embed
from score import get_label_and_color
from config.settings import SEEN_PATH, EXCLUDED_USERS_PATH, PRIORITY_USERS_PATH
from utils import load_user_list, send_discord_message

# ユーザーリスト読み込み
EXCLUDED_USERS = load_user_list(EXCLUDED_USERS_PATH)
PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)

# seen.json 読み込み
if os.path.exists(SEEN_PATH):
    with open(SEEN_PATH, "r", encoding="utf-8") as f:
        seen = set(json.load(f))
else:
    seen = set()

# 作者IDの記録（新規作者判定用）
seen_authors = set()

# 通知条件
def should_notify(item):
    if item["author_id"] in EXCLUDED_USERS:
        return False
    if item["author_id"] in PRIORITY_USERS:
        return True
    if item.get("score", 0) < 60:
        return False
    if item.get("price", 0) > 15000:
        return False
    return True

# 優先度ラベル → 数値
PRIORITY_ORDER = {
    "💌優先": 4,
    "📢特選": 3,
    "🔔おすすめ": 2,
    "📝注目": 1,
    None: 0
}

# 優先度に応じたタイトル
def get_priority_title(items):
    max_score = 0
    max_label = None
    for item in items:
        label, _ = get_label_and_color(item["score"])
        if item["author_id"] in PRIORITY_USERS:
            label = "💌優先"
        score = PRIORITY_ORDER.get(label, 0)
        if score > max_score:
            max_score = score
            max_label = label

    if max_label == "💌優先":
        return "💌SKIMA 優先通知"
    elif max_label == "📢特選":
        return "📢SKIMA 新着通知"
    elif max_label == "🔔おすすめ":
        return "🔔SKIMA 新着通知"
    elif max_label == "📝注目":
        return "📝SKIMA 新着通知"
    else:
        return "SKIMA 新着通知"

# 通知送信（10件ずつまとめて）
def send_embeds_grouped(items):
    embeds = []
    for i, item in enumerate(items):
        embed = build_embed(item)
        embeds.append(embed)

        if len(embeds) == 10:
            send_discord_message({
                "content": None if i != 9 else get_priority_title(items),
                "embeds": embeds
            })
            embeds = []

    if embeds:
        send_discord_message({
            "content": get_priority_title(items),
            "embeds": embeds
        })

# メイン処理
def main():
    items = fetch_items()
    notifies = []

    for item in items:
        if item["id"] in seen:
            continue
        if not should_notify(item):
            continue
        notifies.append(item)
        seen.add(item["id"])
        seen_authors.add(item["author_id"])

    if notifies:
        send_embeds_grouped(notifies)

    # seen.json 保存
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
