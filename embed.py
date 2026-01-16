def build_embed(item, is_priority=False):
    """
    SKIMA の item dict から Discord embed を生成する。
    - is_priority=True の場合は金色で強調
    - rank に応じて色分け
    - 作者名を追加
    - Discord の仕様に完全準拠
    """

    # --- 色分け ---
    if is_priority:
        color = 0xFFD700  # 金色（優先通知）
    else:
        rank = item.get("rank", "")
        if rank == "🔥特選":
            color = 0xFF5555  # 赤
        elif rank == "✨おすすめ":
            color = 0xFFAA00  # オレンジ
        else:
            color = 0x00AAFF  # 通常（青）

    # --- Discord の title は 256 文字まで ---
    title = item.get("title", "")[:256]

    # --- 画像が無い場合は image フィールドを付けない ---
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
