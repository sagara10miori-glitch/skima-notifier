from bs4 import BeautifulSoup
from datetime import datetime
import os

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def safe_get_text(element, default=""):
    """要素が存在しない場合でも安全にテキストを返す"""
    try:
        return element.get_text(strip=True) if element else default
    except Exception:
        return default


def safe_get_attr(element, attr, default=""):
    """要素が存在しない場合でも安全に属性を返す"""
    try:
        return element.get(attr, default) if element else default
    except Exception:
        return default


def parse_items(html: str) -> list[dict]:
    """
    SKIMA の HTML を解析して item リストを返す。
    HTML構造が変わっても最低限の情報で通知できるフェイルセーフ付き。
    """

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        log(f"ERROR: BeautifulSoup parse failed: {e}")
        return []

    items = []

    # SKIMA の商品カード（構造が変わっても柔軟に対応）
    cards = soup.select(".c-itemCard, .item-card, .p-itemCard")

    if not cards:
        log("WARNING: No item cards found. HTML structure may have changed.")
        return []

    for card in cards:
        try:
            # ID（URLから抽出）
            link = card.select_one("a")
            url = safe_get_attr(link, "href", "")
            item_id = url.split("/")[-1] if "/" in url else url

            # タイトル
            title = safe_get_text(card.select_one(".c-itemCard__title, .item-title, .p-itemCard__title"), "タイトル不明")

            # 価格
            price_text = safe_get_text(card.select_one(".c-itemCard__price, .item-price, .p-itemCard__price"), "0")
            price = int("".join(filter(str.isdigit, price_text))) if any(c.isdigit() for c in price_text) else 0

            # 作者
            author = safe_get_text(card.select_one(".c-itemCard__author, .item-author, .p-itemCard__author"), "不明")

            # サムネイル
            thumb = safe_get_attr(card.select_one("img"), "src", "")

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "author": author,
                "url": url,
                "thumb": thumb
            })

        except Exception as e:
            log(f"ERROR: Failed to parse item card: {e}")
            continue

    return items
