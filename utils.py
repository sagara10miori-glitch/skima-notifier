# utils.py
import requests
from urllib.parse import urlparse, parse_qs

def normalize_url(url):
    return url.rstrip("/")

def format_url(url):
    parsed = urlparse(url)
    if "id" in parse_qs(parsed.query):
        item_id = parse_qs(parsed.query)["id"][0]
        return f"🔗 https://skima.jp/dl/detail?id={item_id}"
    return normalize_url(url)

def format_price(price):
    return f"{price:,}円"

def validate_image(url):
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 404:
            return "https://via.placeholder.com/600x400/ffffff/cccccc?text=No+Image"
        return url
    except:
        return "https://via.placeholder.com/600x400/ffffff/cccccc?text=No+Image"

def load_user_list(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
