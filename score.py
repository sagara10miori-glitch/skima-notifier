from datetime import datetime
import os

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


# -----------------------------
# スコア計算（価格ベース）
# -----------------------------
def compute_importance_score(item: dict) -> int:
    """
    価格を基準に重要度スコアを算出。
    安いほどスコアが高い。
    """
    price = item.get("price", 0)

    if price <= 3000:
        return 3
    elif price <= 7000:
        return 2
    elif price <= 12000:
        return 1
    else:
        return 0


# -----------------------------
# ラベル（🔥✨⭐）
# -----------------------------
def importance_label(score: int) -> str:
    if score == 3:
        return "🔥"
    if score == 2:
        return "✨"
    if score == 1:
        return "⭐"
    return ""


# -----------------------------
# Embed 色（赤→青→緑→無色）
# -----------------------------
def importance_color(score: int) -> int:
    if score == 3:
        return 0xFF4444  # 赤
    if score == 2:
        return 0x4488FF  # 青
    if score == 1:
        return 0x44CC88  # 緑
    return 0xCCCCCC      # グレー


# -----------------------------
# 通知タイトル絵文字（📢🔔📝 + 💌）
# -----------------------------
def notification_emoji(score: int, priority: bool) -> str:
    """
    通知タイトルにつける絵文字。
    - スコアに応じて 📢🔔📝
    - 優先通知なら 💌 を追加
    """
    base = ""
    if score == 3:
        base = "📢"
    elif score == 2:
        base = "🔔"
    elif score == 1:
        base = "📝"

    if priority:
        return f"{base}💌" if base else "💌"

    return base
