import os

# -----------------------------------
# SKIMA の監視対象URL
# -----------------------------------
SKIMA_URL = "https://skima.jp/item-list?category_id=1"  
# 必要に応じて変更可能（例：Adoptカテゴリなど）


# -----------------------------------
# Discord Webhook URL（Secretsから取得）
# -----------------------------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

if not WEBHOOK_URL:
    raise ValueError("ERROR: WEBHOOK_URL is not set. Please configure GitHub Secrets.")


# -----------------------------------
# 優先通知の条件（score.py と連携）
# -----------------------------------
# 例：スコア2以上（価格7000円以下）を優先扱いにする
PRIORITY_SCORE_THRESHOLD = 2


# -----------------------------------
# GitHub Actions のランダム遅延（秒）
# -----------------------------------
# 他のワークフローと衝突しにくくするための設定
RANDOM_DELAY_MAX = 5
