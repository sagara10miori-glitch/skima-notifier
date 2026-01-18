def calculate_score(price):
    """
    SKIMA の価格から通知優先度スコアを計算する。
    - 安いほど高スコア
    - 0〜15000円の範囲で自然に差がつく
    """

    # 安全対策：None や 0円でも落ちない
    if price is None:
        return 0

    # 15000円以上は main.py 側で除外されるが念のため
    if price >= 15000:
        return 0

    # スコア計算（安いほど高い）
    # 例：1000円 → 14000点、5000円 → 10000点
    return max(0, 15000 - price)
