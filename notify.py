import requests
import os
import json
import time

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

PIN_FILE = "last_pin.json"


def safe_post(url, headers=None, json_data=None):
    for _ in range(2):
        r = requests.post(url, headers=headers, json=json_data)
        if r.status_code < 500:
            return r
        time.sleep(2)
    return r


def send_webhook_message(title, embeds):
    data = {"content": title, "embeds": embeds}
    return safe_post(WEBHOOK_URL, json_data=data).json()


def send_bot_message(title, embeds):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    data = {"content": title, "embeds": embeds}
    return safe_post(url, headers=headers, json_data=data).json()


def load_last_pin():
    try:
        with open(PIN_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_last_pin(message_id):
    with open(PIN_FILE, "w") as f:
        json.dump({"id": message_id}, f)


def unpin_message(message_id):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    requests.delete(url, headers=headers)


def pin_message(message_id):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    requests.put(url, headers=headers)
