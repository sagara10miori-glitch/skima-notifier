import requests
from bs4 import BeautifulSoup
from config.settings import SKIMA_URL, REQUEST_TIMEOUT
from score import calculate_score

def fetch_items():
    response = requests.get(SKIMA_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # DLページのカード
    cards = soup.select(".c-dlItemCard")

    items = []

    for card in cards:
        try:
            link = card.select_one("a")
            url = "https://skima.jp" + link.get("href")
            item_id = url.rstrip("/").split("/")[-1]

            title = card.select_one(".c-dlItemCard__title").get_text(strip=True)

            price_text = card.select_one(".c-dlItemCard__price").get_text(strip=True)
            price = int(price_text.replace("¥", "").replace(",", ""))

            author = card.select_one(".c-dlItemCard__userName").get_text(strip=True)

            thumbnail = card.select_one("img").get("src")

            score = calculate_score(price)

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "author": author,
                "url": url,
                "thumbnail": thumbnail,
                "score": score,
            })

        except Exception:
            continue

    return items
