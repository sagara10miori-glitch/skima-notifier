def calculate_score(price):
    score = 0

    if price >= 7000:
        score += 2
    elif price >= 3000:
        score += 1

    return score
