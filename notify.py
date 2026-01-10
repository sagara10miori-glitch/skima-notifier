# notify.py

import time
import requests
from config.settings import WEBHOOK_URL

def send_combined_notification(title, embeds):
    payload = {
        "content": title,
        "embeds": embeds
    }

    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code in (401, 404):
        print("[ERROR] Webhook が無効です")
        return

    if response.status_code == 429:
        retry = response.json().get("retry_after", 1000) / 1000
        print(f"[WARN] Discord 429 → {retry}秒待機")
        time.sleep(retry)
        response = requests.post(WEBHOOK_URL, json=payload)

    response.raise_for_status()
