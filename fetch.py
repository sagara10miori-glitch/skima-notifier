import requests
from bs4 import BeautifulSoup
import re
import time

URL = "https://skima.jp/dl/search"

# 安全な一般ブラウザの User-Agent（偽装ではなく互換性のための設定）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}


def fetch_items(priority_only=False):
    html = None

    for attempt in range(2):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                html = r.text
                break
            print(f"[WARN] fetch status={r.status_code}")
            time.sleep(2 + attempt)
        except Exception as e:
            print(f"[WARN] fetch exception: {e}")
            time.sleep(2)

    if not html:
        print("[WARN] failed to fetch item-list")
        return []

    soup = BeautifulSoup(html, "lxml")
    items = []

    # 新しい SKIMA の商品カード構造
    for li in soup.select("li"):
        inner = li.select_one(".inner")
        if not inner:
            continue

        # 画像
        img_tag = inner.select_one(".image img")
        image = img_tag.get("src") if img_tag else None

        # 価格
        price_tag = inner.select_one(".price")
        price_text = price_tag.get_text(strip=True) if price_tag else "0"
        price = int(re.sub(r"\D", "", price_text) or 0)

        # タイトル
        title_tag = inner.select_one("h5 a")
        title = title_tag.get_text(strip=True) if title_tag else "不明"

        # URL
        url = "https://skima.jp" + title_tag.get("href") if title_tag else ""

        # 作者
        author_tag = inner.select_one(".username a")
        author_name = author_tag.get_text(strip=True) if author_tag else "不明"

        author_id = None
        if author_tag:
            href = author_tag.get("href") or ""
            if "id=" in href:
                author_id = href.split("id=")[-1]

        # ランク（SKIMA 新UIでは存在しない可能性あり）
        rank = "通常"

        # 深夜帯フィルタ
        if priority_only and rank not in ("🔥特選", "✨おすすめ"):
            continue

        items.append({
            "id": url.split("=")[-1],  # detail?id=xxxx から取得
            "title": title,
            "price": price,
            "author_id": author_id,
            "author_name": author_name,
            "rank": rank,
            "image": image,
            "url": url,
        })

    print(f"[INFO] fetch_items: {len(items)} items (priority_only={priority_only})")
    return items
