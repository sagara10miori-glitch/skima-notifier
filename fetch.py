# fetch.py

import time
import cloudscraper
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from utils import validate_image, normalize_url

# Cloudflare突破用 scraper
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "firefox",
        "platform": "windows",
        "mobile": False
    }
)

def safe_get(url, retries=3):
    for i in range(retries):
        try:
            r = scraper.get(url, timeout=15)

            # Cloudflare突破後でも 403/503 が出ることがある
            if r.status_code in (403, 503):
                wait = 2 ** i
                print(f"[WARN] {r.status_code} → {wait}秒待機して再試行")
                time.sleep(wait)
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

    # SKIMA の UI 変更に強い柔軟セレクタ
    boxes = soup.select(".item-box")
    if not boxes:
        boxes = soup.select(".item-card")
    if not boxes:
        boxes = soup.select("[class*=item]")
    if not boxes:
        print("[WARN] 作品ボックスが見つかりません")
        return []

    for box in boxes:
        try:
            title_el = safe_select(box, [".item-title", ".title", ".card-title", "[class*=title]"])
            price_el = safe_select(box, [".item-price", ".price", "span:contains('円')"])
            author_el = safe_select(box, [".item-creator", ".creator-name", "[class*=creator]"])
            img_el = box.select_one("img")
            author_link = box.select_one("a[href*='/creator/']")

            if not (title_el and price_el and author_el and img_el and author_link):
                continue

            title = title_el.get_text(strip=True)
            url = normalize_url(box.select_one("a")["href"])
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
        "https://skima.jp/item/list?category=1",
        "https://skima.jp/item/list?category=2",
    ]

    items = []
    with ThreadPoolExecutor(max_workers=5) as exe:
        for result in exe.map(fetch_page, base_urls):
            items.extend(result)

    return items
