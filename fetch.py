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

            if r.status_code == 429:
                wait = 2 ** i
                print(f"[WARN] 429 → {wait}秒待機")
                time.sleep(wait)
                continue

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

    # SKIMA DLページの作品ボックス
    boxes = soup.select("div.inner")
    if not boxes:
        print("[WARN] 作品ボックスが見つかりません")
        return []

    for box in boxes:
        try:
            # URL（相対パス → 絶対URL に修正）
            link_el = box.select_one(".image a[href*='/dl/detail']")
            if not link_el:
                continue

            raw_url = link_el["href"]
            if raw_url.startswith("/"):
                url = "https://skima.jp" + raw_url
            else:
                url = raw_url

            url = normalize_url(url)

            # サムネ
            img_el = box.select_one(".image img")
            thumbnail = validate_image(img_el["src"]) if img_el else None

            # 価格
            price_el = box.select_one(".image .price")
            price = int(price_el.get_text(strip=True).replace("¥", "").replace(",", ""))

            # タイトル
            title_el = box.select_one(".details h5 a")
            title = title_el.get_text(strip=True) if title_el else "無題"

            # 作者
            author_el = box.select_one(".details .username a")
            author = author_el.get_text(strip=True) if author_el else "不明"

            # 作者ID
            author_id = author_el["href"].split("=")[-1] if author_el else "0"

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
        "https://skima.jp/dl/search",
    ]

    items = []
    with ThreadPoolExecutor(max_workers=3) as exe:
        for result in exe.map(fetch_page, base_urls):
            items.extend(result)

    return items
