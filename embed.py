def build_embed(item, is_priority=False):
    color = 0xFFD700 if is_priority else 0x00AAFF

    return {
        "title": item["title"],
        "url": item["url"],
        "color": color,
        "fields": [
            {"name": "価格", "value": f"{item['price']}円"},
            {"name": "優先度", "value": item["rank"]},
        ],
        "image": {"url": item["image"]},
    }
