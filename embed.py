import json

# ⭐注目ユーザー
with open("highlight_users.json", "r", encoding="utf-8") as f:
    HIGHLIGHT_USERS = set(json.load(f))

# 💌優先ユーザー
with open("priority_users.json", "r", encoding="utf-8") as f:
    PRIORITY_USERS = set(json.load(f))


def build_embed(item):
    title = item["title"]
    price = item["price"]
    author = item["author_name"]
    url = item["url"]
    image = item["image"]
    author_id = item["author_id"]

    # -----------------------------
    # ランク判定（あなたの優先度順）
    # -----------------------------
    prefix = ""
    color = 0x66CCFF  # 通常：水色

    if author_id in PRIORITY_USERS:
        prefix = "💌優先"
        color = 0xFF66AA  # ピンク
    elif "🔥" in title:
        prefix = "🔥特選"
        color = 0xFF4444  # 赤
    elif author_id in HIGHLIGHT_USERS:
        prefix = "⭐注目"
        color = 0xFFDD33  # 黄色
    elif "✨" in title:
        prefix = "✨おすすめ"
        color = 0xF28C28  # オレンジ

    if prefix:
        title = f"{prefix} {title}"

    # -----------------------------
    # Gyazo時代のUIを再現したEmbed
    # -----------------------------
    embed = {
        "title": title,
        "url": url,
        "color": color,
        "fields": [
            {
                "name": "価格",
                "value": f"**¥{price:,}**",
                "inline": True
            },
            {
                "name": "作者",
                "value": author,
                "inline": True
            }
        ],
        "image": {
            "url": image
        }
    }

    return embed
