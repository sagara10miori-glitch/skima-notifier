def build_embed(item, is_priority=False):
    # --- 色決定（高速 & 明確化） ---
    if is_priority:
        color = 0xFFD700  # ゴールド
    else:
        rank = item.get("rank")
        color = (
            0xFF5555 if rank == "🔥特選" else
            0xFFAA00 if rank == "✨おすすめ" else
            0x00AAFF
        )

    # --- タイトル（Discord 256文字制限） ---
    title = (item.get("title") or "")[:256]

    # --- 画像（None の場合は付けない） ---
    image_url = item.get("image")

    embed = {
        "title": title,
        "url": item.get("url") or "",
        "color": color,
        "fields": [
            {"name": "価格", "value": f"{item.get('price', 0)}円"},
            {"name": "優先度", "value": item.get("rank") or "不明"},
            {"name": "作者", "value": item.get("author_name") or "不明"},
        ],
    }

    if image_url:
        embed["image"] = {"url": image_url}

    return embed
