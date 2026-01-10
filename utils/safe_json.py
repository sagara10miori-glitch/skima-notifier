import json
import os
from datetime import datetime

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


SEEN_PATH = "storage/seen.json"
MAX_SEEN = 100


# -----------------------------------
# seen.json を安全に読み込む（破損していても復旧）
# -----------------------------------
def load_seen() -> list[str]:
    """
    seen.json を安全に読み込む。
    - ファイルが無い → 新規作成
    - JSON が壊れている → 自動修復
    - リスト以外の形式 → 自動修復
    """

    if not os.path.exists(SEEN_PATH):
        log("INFO: seen.json not found. Creating new file.")
        save_seen([])
        return []

    try:
        with open(SEEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("seen.json is not a list")

        # 文字列化して返す
        return [str(x) for x in data]

    except Exception as e:
        log(f"ERROR: seen.json corrupted. Auto-repairing. ({e})")
        save_seen([])
        return []


# -----------------------------------
# seen.json を安全に保存（最大100件）
# -----------------------------------
def save_seen(seen: list[str]):
    """
    seen.json を保存する。
    - 最大100件に制限
    - 書き込み失敗時もログに記録
    """

    try:
        # 最新100件だけ保持
        trimmed = seen[-MAX_SEEN:]

        os.makedirs("storage", exist_ok=True)

        with open(SEEN_PATH, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False, indent=2)

    except Exception as e:
        log(f"FATAL: Failed to save seen.json ({e})")
