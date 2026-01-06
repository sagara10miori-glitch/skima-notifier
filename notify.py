import requests
from bs4 import BeautifulSoup
import json
import os
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions; contact: example@example.com)"
}

def fetch_html(url, retries=2, delay=2):
    """HTMLを取得（最大2回リトライ）"""
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass

        if attempt < retries:
            time.sleep(delay)

    return None


def parse_item(card):
    """商品カードから情報を抽出する"""

    # タイトル
    title_tag = card.select_one(".details h5 a")
    title = title_tag.text.strip() if title_tag else "タイトル不明"

    # 作者名
    author_tag = card.select_one(".details .username")
    author = author_tag.text.strip() if author_tag else "作者不明"

    # 画像
    img_tag = card.select_one(".image img")
    image = img_tag["src"] if img_tag else None

    # 価格
    price_tag = card.select_one(".price")
    price = price_tag.text.strip() if price_tag else None

    # URL
    link_tag = card.select_one(".image a")
    url = "https://skima.jp" + link_tag["href"] if link_tag else None

    return {
        "title": title,
        "author": author,
        "image": image,
        "price": price,
        "url": url
    }


def get_opt_items(user_id):
    """プロフィールページからDL商品を取得"""
    url = f"https://skima.jp/profile?id={user_id}"
    html = fetch_html(url)

    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    items = []

    for card in soup.select(".inner"):
        link_tag = card.select_one(".image a")
        if not link_tag:
            continue

        href = link_tag.get("href", "")

        # DL商品だけ取得
        if "/dl/detail" not in href:
            continue

        item = parse_item(card)
        items.append(item)

    return items


def send_discord_embed(item):
    """Discord に通知を送る"""
    embed = {
        "title": item["title"],
        "url": item["url"],
        "image": {"url": item["image"]},  # ← 大きめ画像
        "fields": [
            {"name": "価格", "value": item["price"], "inline": True},
            {"name": "作者", "value": item["author"], "inline": True},
            {"name": "商品ページ", "value": item["url"], "inline": False}
        ],
        "color": 0xFF9900
    }

    data = {"embeds": [embed]}
    requests.post(WEBHOOK_URL, json=data)


def main():
    # 前回データ読み込み
    if os.path.exists("last_data.json"):
        with open("last_data.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
    else:
        last_data = {}

    # 監視ユーザー一覧
    with open("users.txt", "r", encoding="utf-8") as f:
        user_ids = [line.strip() for line in f]

    new_last_data = {}

    for uid in user_ids:
        time.sleep(1)  # サーバー負荷軽減

        items = get_opt_items(uid)
        new_last_data[uid] = items

        old_items = last_data.get(uid, [])
        old_urls = {item["url"] for item in old_items}
        new_urls = {item["url"] for item in items}

        added_urls = new_urls - old_urls

        for item in items:
            if item["url"] in added_urls:
                send_discord_embed(item)

    # データ保存
    with open("last_data.json", "w", encoding="utf-8") as f:
        json.dump(new_last_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
