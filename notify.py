import requests
from bs4 import BeautifulSoup
import json
import os
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions; contact: your-email@example.com)"
}

def fetch_html(url, retries=2, delay=2):
    """HTML取得（最大2回リトライ）"""
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass

        if attempt < retries:
            time.sleep(delay)

    return None  # 失敗したら None を返す


def parse_item(card):
    """商品カードから
