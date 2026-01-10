# config/settings.py

import os

# ユーザーリストのパス
PRIORITY_USERS_PATH = "users/priority_users.txt"
EXCLUDE_USERS_PATH = "users/exclude_users.txt"

# main.py で使う統一名（命名を合わせる）
EXCLUDED_USERS_PATH = EXCLUDE_USERS_PATH
SEEN_PATH = "seen.json"

# Discord Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
