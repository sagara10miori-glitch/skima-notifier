import re
from urllib.parse import urlparse


# -----------------------------
# 価格整形（9,000円）
# -----------------------------
def format_price(price: int) -> str:
    """
    価格を「9,000円」のように整形する。
    """
    try:
        return f"{price:,}円"
    except Exception:
        return "0円"


# -----------------------------
# URL整形（🔗 skima.jp/xxxx）
# -----------------------------
def format_url(url: str) -> str:
    """
    URL を「🔗 skima.jp/xxxx」のように短縮表示する。
    """
    if not url:
        return "🔗 URLなし"

    try:
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")
        return f"🔗 skima.jp/{path}"
    except Exception:
        return f"🔗 {url}"
