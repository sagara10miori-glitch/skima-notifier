import cloudscraper
from bs4 import BeautifulSoup
import re
import time

session = cloudscraper.create_scraper()

def fetch_items(priority_only=False):
    url = "https://skima.jp/item-list"

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

    for card in soup.select(".item-card"):
        try:
            item_id = card.get("data-id")

            title_tag = card.select_one(".item-title")
            title = title_tag.get_text(strip=True) if title_tag else "不明"

            price_tag = card.select_one(".item-price")
            price_text = price_tag.get_text(strip=True) if price_tag else "0"
            price = int(re.sub(r"\D", "", price_text))

            author_tag = card.select_one(".ellipsis.username a")
            author_name = author_tag.get_text(strip=True) if author_tag else "不明"

            author_id = None
            if author_tag:
                href = author_tag.get("href", "")
                if "id=" in href:
                    author_id = href.split("id=")[-1]

            rank_tag = card.select_one(".item-rank")
            rank = rank_tag.get_text(strip=True) if rank_tag else "通常"

            img_tag = card.select_one("img")
            image = img_tag.get("src") if img_tag else None

            link_tag = card.select_one("a")
            url = "https://skima.jp" + link_tag.get("href") if link_tag else ""

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
            continue

    return items
