import traceback
from fetch import fetch_page
from parse import parse_items
from notify import send_notification
from utils.safe_json import load_seen, save_seen
from config.settings import SKIMA_URL
from datetime import datetime
import os

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def main():
    try:
        log("=== Notifier started ===")

        # seen.json を安全に読み込み（破損していても自動修復）
        seen = load_seen()

        # SKIMA ページ取得（3回リトライ）
        html = fetch_page(SKIMA_URL)
        if html is None:
            log("ERROR: fetch_page returned None")
            return

        # HTML解析（フェイルセーフ付き）
        items = parse_items(html)
        if not items:
            log("WARNING: parse_items returned empty list")
            return

        new_items = [item for item in items if item["id"] not in seen]

        if not new_items:
            log("No new items.")
            return

        for item in new_items:
            send_notification(item)
            seen.append(item["id"])

        # seen.json を保存（最大100件）
        save_seen(seen)

        log(f"Sent {len(new_items)} notifications.")

    except Exception as e:
        log("FATAL ERROR:")
        log(str(e))
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
