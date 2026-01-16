import cloudscraper
from bs4 import BeautifulSoup
import re
import time

# cloudscraper セッションを使い回す（高速化）
session = cloudscraper.create_scraper()


def fetch_items(priority_only=False):
    """
    SKIMA の新着一覧を取得して item dict のリストを返す。
    priority_only=True の場合は「特選」「おすすめ」のみ抽出。
    """

    url = "https://skima.jp/item-list"

    # --- リトライ付きで HTML を取得 ---
    for attempt in range(3):
        try:
            html = session.get(url, timeout=10).text
            break
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    else:
        return []

    soup = BeautifulSoup(html, "lxml")

    items = []

    # SKIMA のカード構造に対応
    for card in soup.select(".item-card"):
        try:
            # --- ID ---
            item_id = card.get("data-id")

            # --- タイトル ---
            title_tag = card.select_one(".item-title")
            title = title_tag.get_text(strip=True) if title_tag else "不明"

            # --- 価格 ---
            price_tag = card.select_one(".item-price")
            price_text = price_tag.get_text(strip=True) if price_tag else "0"
            price = int(re.sub(r"\D", "", price_text))

            # --- 作者名 & 作者ID ---
            author_tag = card.select_one(".ellipsis.username a")
            author_name = author_tag.get_text(strip=True) if author_tag else "不明"

            author_id = None
            if author_tag:
                href = author_tag.get("href", "")
                if "id=" in href:
                    author_id = href.split("id=")[-1]

            # --- ランク（🔥特選 / ✨おすすめ / 通常） ---
            rank_tag = card.select_one(".item-rank")
            rank = rank_tag.get_text(strip=True) if rank_tag else "通常"

            # --- 画像 ---
            img_tag = card.select_one("img")
            image = img_tag.get("src") if img_tag else None

            # --- URL ---
            link_tag = card.select_one("a")
            url = "https://skima.jp" + link_tag.get("href") if link_tag else ""

            # --- 深夜帯の priority_only フィルタ ---
            if priority_only and rank not in ["🔥特選", "✨おすすめ"]:
                continue

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "author_id": author_id,
                "author_name": author_name,
                "rank": rank,
                "image": image,
                "url": url
            })

        except Exception:
            # HTML 変更などで一部壊れていても落とさない
            continue

    return items
