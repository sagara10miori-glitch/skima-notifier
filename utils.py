import json
import re

def load_user_list(path):
    try:
        with open(path, "r") as f:
            return set(json.load(f))
    except:
        return set()


def normalize_price(text):
    return int(re.sub(r"\D", "", text))
