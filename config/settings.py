import os

print("WEBHOOK_URL raw:", repr(os.getenv("WEBHOOK_URL")))

SKIMA_URL = "https://skima.jp/item-list?category_id=1"
REQUEST_TIMEOUT = 10
CHECK_INTERVAL = 60

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
if not WEBHOOK_URL:
    raise ValueError("ERROR: WEBHOOK_URL is not set. Please configure GitHub Secrets.")

PRIORITY_SCORE_THRESHOLD = 2
RANDOM_DELAY_MAX = 5
