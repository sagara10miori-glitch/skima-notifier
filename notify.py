import requests
from config.settings import WEBHOOK_URL

def send_notification(item):
    embed = {
        "title": item["title"],
        "url": item["url"],
        "thumbnail": {"url": item["thumbnail"]},
        "fields": [
            {"name": "価格", "value": f"¥{item['price']:,}"},
            {"name": "作者", "value": item["author"]},
            {"name": "スコア", "value": str(item["score"])},
        ]
    }

    payload = {"embeds": [embed]}

    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()

    print(f"Sent notification: {item['title']}")
