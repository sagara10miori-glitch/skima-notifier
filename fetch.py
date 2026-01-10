# fetch.py

import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from utils import validate_image, normalize_url

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def safe_get(url, retries=3):
    headers = {"User-Agent": "Mozilla/5.0"}

    for i in range(retries):
        try:
            r = session.get(url, timeout=10, headers=headers)

            if r.status_code == 429:
                wait = (2 ** i)
                print(f"[WARN] 429 → {wait}秒待機")
                time.sleep(wait)
                continue

            if r.status_code == 403:
                headers["User-Agent"] = f"Mozilla/5.0 (Windows NT 10.0; rv:{i+70}.0)"
                print("[WARN] 403 → User-Agent変更して再試行")
                continue

            if r.status_code == 503:
                print("[WARN] 503 → 再試行")
                time.sleep(2)
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

    for box in soup.select(".item-box"):
        try:
            title_el = safe_select(box, [".item-title", ".title", "h1", "[class*=title]"])
            price_el = safe_select(box, [".item-price", "span:contains('円')"])
            author_el = safe_select(box, [".item-creator", "[class*=creator]"])
            img_el = box.select_one("img")
            author_link = box.select_one(".item-creator a")

            if not (title_el and price_el and author_el and img_el and author_link):
                continue

            title = title_el.get_text(strip=True)
            url = normalize_url(box.select_one("a")["href"])
            price = int(price_el.get_text(strip=True).replace("￥", "").replace(",", ""))
            author = author_el.get_text(strip=True)
            author_id = author_link["href"].rstrip("/").split("/")[-1]
            thumbnail = validate_image(img_el["src"])

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

        except:
            continue

    return items


def fetch_page(url):
    r = safe_get(url)
    if not r:
        return []
    return parse_items(r.text)


def fetch_items():
    base_urls = [
        "https://skima.jp/item/list?category=1",
        "https://skima.jp/item/list?category=2",
    ]

    items = []
    with ThreadPoolExecutor(max_workers=5) as exe:
        for result in exe.map(fetch_page, base_urls):
            items.extend(result)

    return items
