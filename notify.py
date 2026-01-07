import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": "SKIMA-Notifier/1.0 (+GitHub Actions)"
}

ORANGE = 0xFFA500
OPT_URL = "https://skima.jp/dl/search?cg=60"


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
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.text
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


def get_items_from_user(user_id):
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


def get_opt_items():
    html = fetch_html(OPT_URL)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    items = []

    for card in soup.select(".inner"):
        items.append(parse_item(card))

    return items


def send_batch_notification(user_new, opt_new):
    """users → タイトル → opt の順で通知（Embed 最大10個）"""

    if not user_new and not opt_new:
        return

    lines = []

    if not is_quiet_hours():
        lines.append("@everyone")

    if opt_new:
        lines.append("📘 OPT販売（8000円以下）")

    content = "\n".join(lines)

    embeds = []

    for item in user_new:
        embeds.append({
            "title": item["title"],
            "url": item["url"],
            "color": ORANGE,
            "image": {"url": item["image"]},
            "description": (
                f"**価格：{item['price']}**\n"
                f"**作者：{item['author']}**\n"
                f"**[商品ページはこちら]({item['url']})**"
            )
        })

    for item in opt_new:
        embeds.append({
            "title": item["title"],
            "url": item["url"],
            "color": ORANGE,
            "image": {"url": item["image"]},
            "description": (
                f"**価格：{item['price']}**\n"
                f"**作者：{item['author']}**\n"
                f"**[商品ページはこちら]({item['url']})**"
            )
        })

    embeds = embeds[:10]

    requests.post(WEBHOOK_URL, json={"content": content, "embeds": embeds})


def main():
    if os.path.exists("last_data.json"):
        with open("last_data.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
    else:
        last_data = {"users": {}, "opt": []}

    with open("users.txt", "r", encoding="utf-8") as f:
        user_ids = [line.strip() for line in f]

    new_last_users = {}
    user_new_items = []

    for uid in user_ids:
        time.sleep(1)
        items = get_items_from_user(uid)
        new_last_users[uid] = items

        old_urls = {item["url"] for item in last_data.get("users", {}).get(uid, [])}
        for item in items:
            if item["url"] not in old_urls:
                user_new_items.append(item)

    opt_items = get_opt_items()
    old_opt_urls = {item["url"] for item in last_data.get("opt", [])}

    opt_new_items = []
    for item in opt_items:
        if item["url"] not in old_opt_urls:
            if item["price_value"] is not None and item["price_value"] <= 8000:
                opt_new_items.append(item)

    opt_new_items.sort(key=lambda x: x["price_value"] or 999999)

    send_batch_notification(user_new_items, opt_new_items)

    new_last_data = {
        "users": new_last_users,
        "opt": opt_items
    }

    with open("last_data.json", "w", encoding="utf-8") as f:
        json.dump(new_last_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
