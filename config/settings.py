import os
print("WEBHOOK_URL raw:", repr(os.getenv("WEBHOOK_URL")))

# -----------------------------------
# SKIMA の監視対象URL
# -----------------------------------
SKIMA_URL = "https://skima.jp/item-list?category_id=1"

# -----------------------------------
# リクエストのタイムアウト（秒）
# -----------------------------------
REQUEST_TIMEOUT = 10

# -----------------------------------
# Discord Webhook URL（Secretsから取得）
# -----------------------------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()

if not WEBHOOK_URL:
    raise ValueError("ERROR: WEBHOOK_URL is not set. Please configure GitHub Secrets.")

# -----------------------------------
# 優先通知の条件
# -----------------------------------
PRIORITY_SCORE_THRESHOLD = 2

# -----------------------------------
# GitHub Actions のランダム遅延（秒）
# -----------------------------------
RANDOM_DELAY_MAX = 5
