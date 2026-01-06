import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions; contact: example@example.com)"
}

ORANGE = 0xFFA500  # Embed の色（オレンジ）


def is_quiet_hours():
    """0:30〜7:30 の間は True"""
    now = datetime.now()
    h, m = now.hour, now.minute

    return (
        (h == 0 and m >= 30) or
        (1 <= h <= 6) or
        (h == 7 and m < 30)
    )


def fetch_html(url, retries=2, delay=2):
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
    title_tag = card.select_one(".details h5 a")
    title = title_tag.text.strip() if title_tag else "タイトル不明"

    author_tag = card.select_one(".details .username")
    author = author_tag.text.strip() if author_tag else "作者不明"

    img_tag = card.select_one(".image img")
    image = img_tag["src"] if img_tag else None

    price_tag = card.select_one(".price")
    price_raw = price_tag.text.strip() if price_tag else None

    # ---- 価格を「◯◯円」形式に統一し、数値も保持 ----
    if price_raw:
        digits = "".join(c for c in price_raw if c.isdigit())
        price_value = int(digits) if digits else None
        price = f"{price_value:,}円" if price_value is not None else price_raw
    else:
        price_value = None
        price = "価格不明"

    link_tag = card.select_one(".image a")
    url = "https://skima.jp" + link_tag["href"] if link_tag else None

    return {
        "title": title,
        "author": author,
        "image": image,
        "price": price,
        "price_value": price_value,
        "url": url
    }


def get_opt_items(user_id):
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

        if "/dl/detail" not in link_tag.get("href", ""):
            continue

        items.append(parse_item(card))

    return items


def send_batch_notification(all_new_items):
    """5000円以下のみ通知・Embed 色はオレンジ固定"""

    if not all_new_items:
        return

    # ---- 5000円以下の商品だけ残す ----
    filtered = [
        item for item in all_new_items
        if item["price_value"] is not None and item["price_value"] <= 5000
    ]

    if not filtered:
        return  # 通知なし

    # ---- 価格の安い順にソート ----
    filtered.sort(key=lambda x: x["price_value"])

    # --- メッセージ本文（content） ---
    if is_quiet_hours():
        content = ""  # 静かな時間帯は @everyone なし
    else:
        content = "@everyone"

    # --- Embed を作成 ---
    embeds = []
    for item in filtered:
        embed = {
            "title": item["title"],
            "url": item["url"],
            "color": ORANGE,  # ← オレンジ固定
            "image": {"url": item["image"]},
            "description": (
                f"**価格：{item['price']}**\n"
                f"**作者：{item['author']}**\n"
                f"**[商品ページはこちら]({item['url']})**"
            )
        }
        embeds.append(embed)

    # --- Discord に送信 ---
    requests.post(WEBHOOK_URL, json={"content": content, "embeds": embeds})


def main():
    if os.path.exists("last_data.json"):
        with open("last_data.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
    else:
        last_data = {}

    with open("users.txt", "r", encoding="utf-8") as f:
        user_ids = [line.strip() for line in f]

    new_last_data = {}
    all_new_items = []

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
                all_new_items.append(item)

    # バッチ通知（Embed）
    send_batch_notification(all_new_items)

    with open("last_data.json", "w", encoding="utf-8") as f:
        json.dump(new_last_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
