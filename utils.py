# utils.py

import requests
from config.settings import WEBHOOK_URL

def send_discord_message(payload):
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
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return url
    except Exception as e:
        print(f"[WARN] サムネイル検証失敗: {e}")
    return None

def normalize_url(url):
    return url.split("&")[0]

def load_user_list(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"[WARN] ユーザーリストが見つかりません: {path}")
        return set()

def format_url(url):
    return f"<{url}>" if url else "―"

def format_price(price):
    if price is None:
        return "―"
    return f"¥{price:,}"
