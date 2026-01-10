# score.py

def calculate_score(price):
    if price <= 5000:
        return 3
    elif price <= 8000:
        return 2
    elif price <= 10000:
        return 1
    elif price <= 12000:
        return 0
    else:
        return 0

def get_label_and_color(score):
    if score == 3:
        return "🔥特選", 0xE74C3C
    elif score == 2:
        return "✨おすすめ", 0x3498DB
    else:
        return "⭐注目", 0x2ECC71
