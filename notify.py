import requests
import time
from datetime import datetime
import os

from embed import build_embed
from score import compute_importance_score, notification_emoji
from config.settings import WEBHOOK_URL
from utils.safe_json import load_seen
from utils.format import format_url

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


# -----------------------------------
# ユーザーリスト読み込み（強化版）
# -----------------------------------
def load_txt_list(path: str) -> list[str]:
    """空行・重複・全角/半角スペースを吸収して安全に読み込む"""
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    cleaned = set()
    for line in lines:
        line = line.strip().replace("　", "")  # 全角スペース除去
        if line:
            cleaned.add(line)

    return list(cleaned)


def load_priority_users() -> list[str]:
    return load_txt_list("storage/priority_users.txt")


def load_exclude_users() -> list[str]:
    return load_txt_list("storage/exclude_users.txt")


# -----------------------------------
# Webhook送信（再送＋レート制限）
# -----------------------------------
def post_webhook(payload: dict, retries: int = 2) -> bool:
    """
    Discord Webhook に送信する。
    - 最大2回再送
    - レート制限時は自動で待機
    """

    for attempt in range(1, retries + 2):
        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)

            # 成功
            if response.status_code in (200, 204):
                return True

            # レート制限
            if response.status_code == 429:
                retry_after = response.json().get("retry_after", 1)
                log(f"RATE LIMIT: waiting {retry_after}s")
                time.sleep(retry_after)
                continue

            log(f"WARNING: Webhook status {response.status_code} (attempt {attempt})")

        except Exception as e:
            log(f"ERROR: Webhook exception on attempt {attempt}: {e}")

        time.sleep(1.5)

    log("FATAL: Webhook failed after all retries.")
    return False


# -----------------------------------
# 通知送信（優先/除外ユーザー対応）
# -----------------------------------
def send_notification(item: dict):
    priority_users = load_priority_users()
    exclude_users = load_exclude_users()

    # 通知対象ユーザー = 優先 − 除外
    target_users = [u for u in priority_users if u not in exclude_users]

    # 優先通知判定（価格ベース）
    score = compute_importance_score(item)
    is_priority = score >= 2  # 例：スコア2以上を優先扱い

    # 通知タイトル絵文字
    emoji = notification_emoji(score, is_priority)

    # Embed生成
    embed = build_embed(item)

    # メッセージ本文
    content_lines = []

    # メンション
    if target_users:
        mentions = " ".join([f"<@{uid}>" for uid in target_users])
        content_lines.append(mentions)

    # 絵文字タイトル
    content_lines.append(f"{emoji} 新着通知")

    payload = {
        "content": "\n".join(content_lines),
        "embeds": [embed]
    }

    # Webhook送信（再送付き）
    success = post_webhook(payload)

    if success:
        log(f"Sent notification: {item.get('title')}")
    else:
        log(f"FAILED to send notification: {item.get('title')}")
