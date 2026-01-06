import requests
from bs4 import BeautifulSoup
import json
import os
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions; contact: example@example.com)"
}

# 色リスト（ユーザー順で割り当て）
COLOR_LIST = [
    0xFF9900,  # オレンジ
    0x66CCFF,  # 水色
    0xCC66FF,  # 紫
    0x33CC99,  # 緑
    0xFF6666,  # 赤
    0x6699FF,  # 青
    0xFFCC33,  # 黄色
    0xFF99CC,  # ピンク
    0x999999,  # グレー
    0x00CCFF,  # シアン
]

CUTE_DIVIDER = "✦━━━━━━━━━━━━✦"


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

    title_tag = card.select_one(".details h5 a")
    title = title_tag.text.strip() if title_tag else "タイトル不明"

    author_tag = card.select_one(".details .username")
    author = author_tag.text.strip() if author_tag else "作者不明"

    img_tag = card.select_one(".image img")
    image = img_tag["src"] if img_tag else None

    price_tag = card.select_one(".price")
    price = price_tag.text.strip() if price_tag else None

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

        if "/dl/detail" not in href:
            continue

        item = parse_item(card)
        items.append(item)

    return items


def send_discord_embed(item, color):
    """Discord に通知を送る"""

    content = "@everyone"  # ← ここで everyone 通知

    embed = {
        "title": item["title"],
        "url": item["url"],
        "image": {"url": item["image"]},

        "description": (
            f"**価格：{item['price']}**\n"
            f"**作者：{item['author']}**\n"
            f"{item['url']}\n\n"
            f"{CUTE_DIVIDER}"
        ),

        "color": color
    }

    requests.post(WEBHOOK_URL, json={"content": content, "embeds": [embed]})


def main():
    if os.path.exists("last_data.json"):
        with open("last_data.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
    else:
        last_data = {}

    with open("users.txt", "r", encoding="utf-8") as f:
        user_ids = [line.strip() for line in f]

    user_colors = {
        uid: COLOR_LIST[i % len(COLOR_LIST)]
        for i, uid in enumerate(user_ids)
    }

    new_last_data = {}

    for uid in user_ids:
        time.sleep(1)

        items = get_opt_items(uid)
        new_last_data[uid] = items

        old_items = last_data.get(uid, [])
        old_urls = {item["url"] for item in old_items}
        new_urls = {item["url"] for item in items}

        added_urls = new_urls - old_urls

        for item in items:
            if item["url"] in added_urls:
                send_discord_embed(item, user_colors[uid])

    with open("last_data.json", "w", encoding="utf-8") as f:
        json.dump(new_last_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
