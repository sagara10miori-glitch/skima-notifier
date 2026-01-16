import requests
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")


# --- Webhook 通常通知 --------------------------------------------------------

def send_webhook_message(title, embeds):
    data = {
        "content": title,
        "embeds": embeds
    }
    r = requests.post(WEBHOOK_URL, json=data)
    return r.json()


# --- Bot 優先通知 ------------------------------------------------------------

def send_bot_message(title, embeds):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }
    data = {
        "content": title,
        "embeds": embeds
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()  # message_id を返す


# --- ピン止め ---------------------------------------------------------------

def pin_message(message_id):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }
    requests.put(url, headers=headers)
