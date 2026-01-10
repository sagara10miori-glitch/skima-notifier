# score.py

def calculate_score(price):
    """価格のみでスコアを決定"""
    if price >= 7000:
        return 3
    elif price >= 4000:
        return 2
    elif price >= 2000:
        return 1
    else:
        return 0


def get_label_and_color(score):
    """スコアに応じてラベルと色を返す"""
    if score >= 3:
        return "🔥特選", 0xE74C3C  # 赤
    elif score == 2:
        return "✨おすすめ", 0x3498DB  # 青
    elif score == 1:
        return "⭐注目", 0x2ECC71  # 緑
    else:
        return None, 0x95A5A6  # ラベルなし
