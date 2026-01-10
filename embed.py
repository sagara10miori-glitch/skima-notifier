# embed.py

from utils import format_url, format_price, validate_image
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

    if label:
        fields.append({
            "name": "優先度",
            "value": label,
            "inline": True
        })

    fields.append({
        "name": "価格",
        "value": format_price(item["price"]),
        "inline": True
    })

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
        "image": {
            "url": validate_image(item["thumbnail"])
        },
        "footer": {
            "text": "────────"
        }
    }
