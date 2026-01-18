import requests
import os
import json
import time

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

PIN_FILE = "last_pin.json"


def safe_post(url, headers=None, json_data=None):
    """Discord API への POST を安全に行う（3回リトライ）"""
    if not url:
        return None

    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=json_data, timeout=10)

            # 成功
            if 200 <= r.status_code < 300:
                return r

            # レートリミット対応
            if r.status_code == 429:
                retry_after = r.json().get("retry_after", 2)
                time.sleep(retry_after)
                continue

        except Exception:
            time.sleep(2)

        # 次のリトライまで少し待つ
        time.sleep(1.5 * (attempt + 1))

    return r  # 最後のレスポンスを返す


def send_webhook_message(title, embeds):
    """通常通知（Webhook）"""
    if not WEBHOOK_URL:
        return {"error": "WEBHOOK_URL not set"}

    data = {"content": title, "embeds": embeds}
    r = safe_post(WEBHOOK_URL, json_data=data)

    try:
        return r.json() if r else {"error": "request failed"}
    except Exception:
        return {"error": "invalid response"}


def send_bot_message(title, embeds):
    """優先通知（Bot API）"""
    if not BOT_TOKEN or not CHANNEL_ID:
        return {"error": "Bot credentials not set"}

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    data = {"content": title, "embeds": embeds}

    r = safe_post(url, headers=headers, json_data=data)

    try:
        return r.json() if r else {"error": "request failed"}
    except Exception:
        return {"error": "invalid response"}


def load_last_pin():
    """最後にピンしたメッセージIDを読み込む"""
    try:
        with open(PIN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_last_pin(message_id):
    """ピンしたメッセージIDを保存"""
    try:
        with open(PIN_FILE, "w") as f:
            json.dump({"id": message_id}, f)
    except Exception:
        pass


def unpin_message(message_id):
    """既存のピンを解除"""
    if not BOT_TOKEN or not CHANNEL_ID:
        return

    if not message_id:
        return

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    safe_post(url, headers=headers)


def pin_message(message_id):
    """新しいメッセージをピン固定"""
    if not BOT_TOKEN or not CHANNEL_ID:
        return

    if not message_id:
        return

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    safe_post(url, headers=headers)
