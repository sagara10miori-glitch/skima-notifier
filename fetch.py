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
        except:
            time.sleep(1.5 * (attempt + 1))
    else:
        return []

    soup = BeautifulSoup(html, "lxml")

    items = []

    for card in soup.select(".item-card"):
        try:
            item_id = card.get("data-id")
            title = card.select_one(".item-title").get_text(strip=True)

            price_text = card.select_one(".item-price").get_text(strip=True)
            price = int(re.sub(r"\D", "", price_text))

            author_id = card.select_one(".item-user").get("data-user-id")
            rank = card.select_one(".item-rank").get_text(strip=True)
            image = card.select_one("img").get("src")
            url = "https://skima.jp" + card.select_one("a").get("href")

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "author_id": author_id,
                "rank": rank,
                "image": image,
                "url": url
            })

        except:
            continue

    return items
