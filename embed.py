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

    # ① 優先ユーザー（author_id が PRIORITY_USERS に含まれるかどうかは main.py 側で判定）
    if item.get("is_priority"):
        prefix = "💌優先"
        color = 0xFF66AA  # ピンク

    # ② タイトルに🔥（最優先の特選）
    elif "🔥" in title:
        prefix = "🔥特選"
        color = 0xFF4444  # 赤

    # ③ 価格で特選（3000円以下）
    elif price <= 3000:
        prefix = "🔥特選"
        color = 0xFF4444  # 赤

    # ④ 価格で注目（5000円以下）
    elif price <= 5000:
        prefix = "⭐注目"
        color = 0xFFDD33  # 黄色

    # ⑤ 価格でおすすめ（10000円以下）
    elif price <= 10000:
        prefix = "✨おすすめ"
        color = 0xF28C28  # オレンジ

    # ⑥ 通常
    else:
        prefix = ""
        color = 0x66CCFF  # 水色

    # prefix をタイトルに付ける
    final_title = f"{prefix} {title}" if prefix else title

    embed = {
        "title": final_title,
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

    return embed, prefix
