# embed.py

from utils import format_url
from score import get_label_and_color

def build_embed(item):
    label, color = get_label_and_color(item["score"])

    framed_title = f"《  {item['title']}  》"

    fields = [
        {
            "name": "リンク",
            "value": format_url(item["url"]),
            "inline": False
        }
    ]

    # ラベルがある場合のみ「優先度」フィールドを追加
    if label:
        fields.append({
            "name": "優先度",
            "value": label,
            "inline": True
        })

    # 価格フィールド（ラベルは含めない）
    fields.append({
        "name": "価格",
        "value": f"¥{item['price']:,}",
        "inline": True
    })

    # 作者フィールド
    fields.append({
        "name": "作者",
        "value": item["author"],
        "inline": True
    })

    return {
        "title": framed_title,
        "url": item["url"],
        "color": color,
        "fields": fields,

        # 小さいサムネイルは削除
        # 大きい画像のみ
        "image": {
            "url": item["thumbnail"]
        }
    }
