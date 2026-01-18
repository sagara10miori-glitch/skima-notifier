def build_embed(item, is_priority=False):
    if is_priority:
        color = 0xFFD700
    else:
        rank = item.get("rank", "")
        if rank == "🔥特選":
            color = 0xFF5555
        elif rank == "✨おすすめ":
            color = 0xFFAA00
        else:
            color = 0x00AAFF

    title = item.get("title", "")[:256]

    image_url = item.get("image")
    image_block = {"url": image_url} if image_url else None

    embed = {
        "title": title,
        "url": item.get("url", ""),
        "color": color,
        "fields": [
            {"name": "価格", "value": f"{item.get('price', 0)}円"},
            {"name": "優先度", "value": item.get("rank", "不明")},
            {"name": "作者", "value": item.get("author_name", "不明")},
        ],
    }

    if image_block:
        embed["image"] = image_block

    return embed
