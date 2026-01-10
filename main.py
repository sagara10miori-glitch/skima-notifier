# main.py

from score import calculate_score
from embed import build_embed
from notify import send_combined_notification
from utils import load_seen_ids, save_seen_ids, load_user_list
from config.settings import PRIORITY_USERS, EXCLUDE_USERS


def determine_notification_title(items, PRIORITY_USERS):
    # 優先ユーザーが含まれるか？
    has_priority = any(item["author"] in PRIORITY_USERS for item in items)

    # 最上位ラベルを探す
    top_label = None
    for item in items:
        score = item["score"]
        if score >= 3:
            top_label = "🔥"
            break
        elif score == 2 and top_label != "🔥":
            top_label = "✨"
        elif score == 1 and top_label not in ("🔥", "✨"):
            top_label = "⭐"

    emoji_map = {
        "🔥": "📢",
        "✨": "🔔",
        "⭐": "📝",
        None: ""
    }

    icon = emoji_map[top_label]

    # @everyone 条件
    should_ping = (
        has_priority or
        top_label in ("🔥", "✨")
    )

    # 通知タイトル
    if has_priority:
        title = "💌SKIMA　優先通知"
    else:
        if icon == "":
            title = "SKIMA　新着通知"
        else:
            title = f"{icon}SKIMA　新着通知"

    # @everyone 付与
    if should_ping:
        title = f"@everyone\n{title}"

    return title


def main():
    seen_ids = load_seen_ids()

    items = fetch_items()
    if not items:
        return

    # 新規のみ
    new_items = [i for i in items if i["id"] not in seen_ids]

    # 除外ユーザー削除
    new_items = [i for i in new_items if i["author"] not in EXCLUDE_USERS]

    # スコア計算（価格のみ）
    for item in new_items:
        item["score"] = calculate_score(item["price"])

    # 並び順：優先ユーザー → スコア降順
    new_items.sort(
        key=lambda x: (
            x["author"] in PRIORITY_USERS,
            x["score"]
        ),
        reverse=True
    )

    # 最大10件
    new_items = new_items[:10]

    if not new_items:
        return

    # 通知タイトル決定
    title = determine_notification_title(new_items, PRIORITY_USERS)

    # embed をまとめて生成
    embeds = [build_embed(item) for item in new_items]

    # 1メッセージで送信
    send_combined_notification(title, embeds)

    # seen.json 更新
    for item in new_items:
        seen_ids.append(item["id"])
    save_seen_ids(seen_ids)
