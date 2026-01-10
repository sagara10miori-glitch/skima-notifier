from utils import format_url, format_price, validate_image
from score import get_label_and_color
from config.settings import PRIORITY_USERS_PATH
from utils import load_user_list

# 優先ユーザー一覧を読み込み
PRIORITY_USERS = load_user_list(PRIORITY_USERS_PATH)

def build_embed(item):
    # 優先ユーザーなら強制的に「💌優先」
    if item["author_id"] in PRIORITY_USERS:
        label = "💌優先"
        color = 0xE91E63  # ピンク系
    else:
        label, color = get_label_and_color(item["score"])

    if color is None:
        color = 0x5865F2  # Discordブルー

    title = item.get("title") or "無題"
    framed_title = f"《  {title}  》"

    url = item.get("url") or "https://skima.jp/"

    fields = [
        {
            "name": "リンク",
            "value": format_url(url),
            "inline": False
        }
    ]

    if label:
        fields.append({
            "name": "優先度",
            "value": label,
            "inline": True
        })

    price = item.get("price", 0)

    fields.append({
        "name": "価格",
        "value": format_price(price),
        "inline": True
    })

    author = item.get("author") or "不明"

    fields.append({
        "name": "作者",
        "value": author,
        "inline": True
    })

    thumbnail = validate_image(item.get("thumbnail"))
    if not thumbnail:
        thumbnail = "https://skima.jp/assets/img/common/noimage.png"

    return {
        "title": framed_title,
        "url": url,
        "color": color,
        "fields": fields,
        "image": {
            "url": thumbnail
        }
        # ★ 区切り線（footer）を完全削除 ★
    }
