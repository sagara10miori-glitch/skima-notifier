import requests
import time
from datetime import datetime
import os

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def fetch_page(url: str, retries: int = 3, delay: float = 1.5) -> str | None:
    """
    SKIMAページを取得する。
    - 最大3回リトライ
    - 失敗時はログに記録
    - 最終的に取得できなければ None を返す
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.text

            log(f"WARNING: fetch_page status {response.status_code} (attempt {attempt})")

        except Exception as e:
            log(f"ERROR: fetch_page exception on attempt {attempt}: {e}")

        time.sleep(delay)

    log("FATAL: fetch_page failed after all retries.")
    return None
