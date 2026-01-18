import requests
import os
import json
import time

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

PIN_FILE = "last_pin.json"


def safe_post(url, headers=None, json_data=None):
    if not url:
        return None

    last_response = None

    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=json_data, timeout=10)
            last_response = r

            if 200 <= r.status_code < 300:
                return r

            if r.status_code == 429:
                try:
                    retry_after = r.json().get("retry_after", 2)
                except Exception:
                    retry_after = 2
                time.sleep(retry_after)
                continue

        except Exception:
            time.sleep(2)

        time.sleep(1.5 * (attempt + 1))

    return last_response


def _safe_json(r):
    if not r:
        return {"error": "request failed"}
    try:
        return r.json()
    except Exception:
        return {"error": f"invalid response: {r.status_code}"}


def send_webhook_message(title, embeds):
    if not WEBHOOK_URL:
        return {"error": "WEBHOOK_URL not set"}

    data = {"content": title, "embeds": embeds}
    r = safe_post(WEBHOOK_URL, json_data=data)
    return _safe_json(r)


def send_bot_message(title, embeds):
    if not BOT_TOKEN or not CHANNEL_ID:
        return {"error": "Bot credentials not set"}

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    data = {"content": title, "embeds": embeds}

    r = safe_post(url, headers=headers, json_data=data)
    return _safe_json(r)


def load_last_pin():
    try:
        with open(PIN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_last_pin(message_id):
    try:
        with open(PIN_FILE, "w") as f:
            json.dump({"id": message_id}, f)
    except Exception:
        pass


def unpin_message(message_id):
    if not BOT_TOKEN or not CHANNEL_ID or not message_id:
        return

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    safe_post(url, headers=headers)


def pin_message(message_id):
    if not BOT_TOKEN or not CHANNEL_ID or not message_id:
        return

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    safe_post(url, headers=headers)
