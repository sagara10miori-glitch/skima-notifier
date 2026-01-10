from score import importance_label, importance_color
from utils.format import format_price, format_url
from datetime import datetime
import os

LOG_PATH = "logs/notifier.log"


def log(message: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def build_embed(item: dict) -> dict:
    """
    Discord Embed を構築する。
    あなたの美学に合わせた最終デザイン。
    """

    title = item.get("title", "タイトル不明")
    price = item.get("price", 0)
    author = item.get("author", "不明")
    url = item.get("url", "")
    thumb = item.get("thumb", "")

    # スコア → ラベル・色
    from score import compute_importance_score
    score = compute_importance_score(item)
    label = importance_label(score)
    color = importance_color(score)

    # タイトルを額縁スタイルに
    framed_title = f"《  {title}  》"

    # ラベルがあればタイトルに付与
    if label:
        framed_title = f"{label} {framed_title}"

    embed = {
        "title": framed_title,
        "url": url,
        "color": color,
        "fields": [
            {
                "name": "リンク",
                "value": format_url(url),
                "inline": False
            },
            {
                "name": "価格",
                "value": format_price(price),
                "inline": True
            },
            {
                "name": "作者",
                "value": author,
                "inline": True
            }
        ],
        "thumbnail": {
            "url": thumb
        }
    }

    return embed
