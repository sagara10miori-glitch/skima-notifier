import os

PRIORITY_USERS_PATH = "users/priority_users.txt"
EXCLUDE_USERS_PATH = "users/exclude_users.txt"

# 価格上限（通知しない上限）
PRICE_LIMIT = 999999  # 好きな値に変更可能

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
