import json
import re
from json import JSONDecodeError


def load_user_list(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            return set(data)
        return set()

    except (FileNotFoundError, JSONDecodeError):
        return set()


def normalize_price(text):
    if not text:
        return 0

    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else 0
