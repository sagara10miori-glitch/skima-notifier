import requests
from bs4 import BeautifulSoup
import json
import os
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions; contact: your-email@example.com)"
}

def fetch_html(url, retries=2, delay=2):
    """HTML取得（最大2回リトライ）"""
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass

        if attempt < retries:
            time.sleep(delay)

    return None  # 失敗したら None を返す


def get_opt_items(user_id):
    url = f"https://skima.jp/profile?id={user_id}"
    html = fetch_html(url)

    if html is None:
        return []  # 取得失敗時は空リスト

    soup = BeautifulSoup(html, "html.parser")
    items = []

    for card in soup.select("div.image"):
        link_tag = card.select_one("a")
        if not link_tag:
            continue

        href = link_tag.get("href", "")

        # opt販売（DL商品）は /dl/detail を含む
        if "/dl/detail" not in href:
            continue

        img_tag = card.select_one("img")
        price_tag = card.select_one(".price")

        # タイトル取得
        title_tag = None

        # <a> 内にタイトルがある場合
        for child in link_tag.find_all():
            if child.name not in ["img", "a"] and child.text.strip():
                title_tag = child
                break

        # <a> の外にタイトルがある場合
        if not title_tag:
            for sibling in card.find_all():
                if sibling.name not in ["img", "a", "div"] and sibling.text.strip():
                    title_tag = sibling
                    break

        title = title_tag.text.strip() if title_tag else "タイトル不明"

        item = {
            "url": "https://skima.jp" + href,
            "image": img_tag["src"] if img_tag else None,
            "price": price_tag.text.strip() if price_tag else None,
            "title": title
        }

        items.append(item)

    return items


def send_discord_embed(item, user_id):
    embed = {
        "title": item["title"],
        "url": item["url"],
        "thumbnail": {"url": item["image"]},
        "fields": [
            {"name": "価格", "value": item["price"], "inline": True},
            {"name": "ユーザーID", "value": str(user_id), "inline": True},
            {"name": "商品ページ", "value": item["url"], "inline": False}
        ],
        "color": 0xFF9900
    }

    data = {"embeds": [embed]}
    requests.post(WEBHOOK_URL, json=data)


def main():
    if os.path.exists("last_data.json"):
        with open("last_data.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
    else:
        last_data = {}

    with open("users.txt", "r", encoding="utf-8") as f:
        user_ids = [line.strip() for line in f]

    new_last_data = {}

    for uid in user_ids:
        # --- サーバー負荷軽減のためのスリープ ---
        time.sleep(1)

        items = get_opt_items(uid)
        new_last_data[uid] = items

        old_items = last_data.get(uid, [])
        old_urls = {item["url"] for item in old_items}
        new_urls = {item["url"] for item in items}

        added_urls = new_urls - old_urls

        for item in items:
            if item["url"] in added_urls:
                send_discord_embed(item, uid)

    with open("last_data.json", "w", encoding="utf-8") as f:
        json.dump(new_last_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
