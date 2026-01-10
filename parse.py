import requests
from bs4 import BeautifulSoup
from config.settings import SKIMA_URL, REQUEST_TIMEOUT


def fetch_items():
    """
    SKIMA の新着商品一覧ページを取得し、
    各商品を {id, title, price, author, url, thumbnail, score} の dict にして返す。
    """

    response = requests.get(SKIMA_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 商品カードを取得（SKIMA の DOM 構造に合わせて調整）
    cards = soup.select(".c-itemCard")
    items = []

    for card in cards:
        try:
            # 商品ID（URLの末尾から抽出）
            link = card.select_one("a")
            url = link.get("href")
            item_id = url.rstrip("/").split("/")[-1]

            # タイトル
            title = card.select_one(".c-itemCard__title").get_text(strip=True)

            # 価格
            price_text = card.select_one(".c-itemCard__price").get_text(strip=True)
            price = int(price_text.replace("¥", "").replace(",", ""))

            # 作者
            author = card.select_one(".c-itemCard__userName").get_text(strip=True)

            # サムネイル
            thumbnail = card.select_one("img").get("src")

            # スコア（あなたのロジックに合わせて計算）
            score = 0
            if price >= 7000:
                score += 2
            elif price >= 3000:
                score += 1

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
            # 1件壊れていても全体が止まらないようにする
            continue

    return items
