# fetch.py

import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from utils import validate_image, normalize_url

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

def safe_get(url, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, timeout=10)

            # 429 → 待機
            if r.status_code == 429:
                wait = 2 ** i
                print(f"[WARN] 429 → {wait}秒待機")
                time.sleep(wait)
                continue

            # 403 → UA変更して再試行
            if r.status_code == 403:
                print("[WARN] 403 → User-Agent変更して再試行")
                session.headers.update({
                    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; rv:{i+70}.0)"
                })
                continue

            return r

        except Exception as e:
            print(f"[ERROR] リクエスト失敗 {i+1}/{retries}: {e}")
            time.sleep(2)

    return None


def safe_select(soup, selectors):
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el
    return None


def parse_items(html):
    soup = BeautifulSoup(html, "lxml")
    items = []

    # DLページの作品ボックス
    boxes = soup.select(".dl-item")
    if not boxes:
        boxes = soup.select("[class*=dl]")
    if not boxes:
        print("[WARN] 作品ボックスが見つかりません")
        return []

    for box in boxes:
        try:
            title_el = safe_select(box, [".item-title", ".title", "[class*=title]"])
            price_el = safe_select(box, [".item-price", ".price", "span:contains('円')"])
            author_el = safe_select(box, [".item-creator", "[class*=creator]"])
            img_el = box.select_one("img")
            author_link = box.select_one("a[href*='/creator/']")
            link_el = box.select_one("a[href*='/dl/']")

            if not (title_el and price_el and author_el and img_el and author_link and link_el):
                continue

            title = title_el.get_text(strip=True)
            url = normalize_url(link_el["href"])
            price = int(price_el.get_text(strip=True).replace("￥", "").replace(",", ""))
            author = author_el.get_text(strip=True)
            author_id = author_link["href"].rstrip("/").split("/")[-1]
            thumbnail = validate_image(img_el["src"])

            # 異常価格はスキップ
            if price <= 0 or price == 999999:
                continue

            items.append({
                "id": url,
                "title": title,
                "url": url,
                "price": price,
                "author": author,
                "author_id": author_id,
                "thumbnail": thumbnail
            })

        except Exception as e:
            print("[ERROR] parse error:", e)
            continue

    return items


def fetch_page(url):
    r = safe_get(url)
    if not r:
        return []
    return parse_items(r.text)


def fetch_items():
    base_urls = [
        "https://skima.jp/dl/search",   # ← これだけでOK
    ]

    items = []
    with ThreadPoolExecutor(max_workers=3) as exe:
        for result in exe.map(fetch_page, base_urls):
            items.extend(result)

    return items
