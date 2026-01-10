import requests
from bs4 import BeautifulSoup
from config.settings import SKIMA_URL, REQUEST_TIMEOUT
from score import calculate_score

def fetch_items():
    response = requests.get(SKIMA_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 商品カードは .inner
    cards = soup.select(".inner")

    items = []

    for card in cards:
        try:
            # URL
            link = card.select_one(".image a")
            url = "https://skima.jp" + link.get("href")
            item_id = url.split("id=")[-1]

            # サムネイル
            thumbnail = card.select_one(".image img").get("src")

            # 価格
            price_text = card.select_one(".image .price").get_text(strip=True)
            price = int(price_text.replace("¥", "").replace(",", ""))

            # タイトル
            title = card.select_one(".details h5 a").get_text(strip=True)

            # 作者
            author = card.select_one(".details .username a").get_text(strip=True)

            # スコア
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
