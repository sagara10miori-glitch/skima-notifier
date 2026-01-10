# utils.py

import requests
from config.settings import WEBHOOK_URL

def send_discord_message(payload):
    """
    Discord Webhook にメッセージまたは embed を送信する。
    payload: dict
        - content: str（任意）
        - embeds: list（任意）
    """
    if not WEBHOOK_URL:
        print("[ERROR] WEBHOOK_URL が設定されていません")
        return

    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        if r.status_code >= 400:
            print(f"[ERROR] Discord送信失敗: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[ERROR] Discord送信エラー: {e}")


def validate_image(url):
    """
    URLが有効な画像かどうかをHEADリクエストで確認し、問題なければ返す。
    """
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return url
    except Exception as e:
        print(f"[WARN] サムネイル検証失敗: {e}")
    return None


def normalize_url(url):
    """
    URLの末尾に不要なパラメータがあれば削除する（例: &from=xxx）
    """
    return url.split("&")[0]


def load_user_list(path):
    """
    ユーザーIDリスト（priority_users.txt / exclude_users.txt）を読み込む
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"[WARN] ユーザーリストが見つかりません: {path}")
        return set()
