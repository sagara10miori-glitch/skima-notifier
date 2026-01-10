# config/settings.py
import os

PRIORITY_USERS_PATH = "users/priority_users.txt"
EXCLUDE_USERS_PATH = "users/exclude_users.txt"

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
