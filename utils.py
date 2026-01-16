import json
import re
from json import JSONDecodeError


def load_user_list(path):
    """
    JSON 配列（["123", "456"]）を読み込んで set にして返す。
    - ファイルが無い場合は空集合
    - JSON が壊れている場合も空集合
    - 配列以外（dict など）は無視
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)

        # 配列以外は無視
        if isinstance(data, list):
            return set(data)
        return set()

    except (FileNotFoundError, JSONDecodeError):
        return set()


def normalize_price(text):
    """
    数字以外を除去して int に変換。
    空文字や None の場合は 0 を返す。
    """
    if not text:
        return 0

    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else 0
