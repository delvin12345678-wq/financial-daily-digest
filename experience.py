"""用戶經驗分級 — 從持股數、方案、訂閱年資估算投資經驗。

經驗分 = 方案分 + 數量分 + 年資分  (0~100)
  方案分:free 0 / pro 18 / premium 30
  數量分:50 × (1 − e^(−N/7))      N = 美股數 + 台股數
  年資分:20 × (1 − e^(−天數/120))  缺日期時以 0 計(偏保守,寧可多給引導)
分級:<30 新手 / 30–66 一般 / ≥66 老手
"""

import math

PLAN_POINTS = {"free": 0, "pro": 18, "premium": 30}


def experience_score(us_count, tw_count, plan="free", age_days=0):
    n = (us_count or 0) + (tw_count or 0)
    plan_pts = PLAN_POINTS.get((plan or "free").lower(), 0)
    count_pts = 50 * (1 - math.exp(-n / 7))
    tenure_pts = 20 * (1 - math.exp(-max(age_days or 0, 0) / 120))
    return round(plan_pts + count_pts + tenure_pts, 1)


def experience_tier(us_count, tw_count, plan="free", age_days=0):
    score = experience_score(us_count, tw_count, plan, age_days)
    if score < 30:
        tier = "新手"
    elif score < 66:
        tier = "一般"
    else:
        tier = "老手"
    return score, tier


if __name__ == "__main__":
    cases = [
        ("Free 1 檔,新", 1, 0, "free", 7),
        ("Free 3 檔,1 年", 3, 0, "free", 365),
        ("Pro 14 檔,半年", 10, 4, "pro", 180),
        ("Premium 25 檔,8 個月", 18, 7, "premium", 240),
    ]
    for label, us, tw, plan, age in cases:
        score, tier = experience_tier(us, tw, plan, age)
        print(f"{label:22s} → {score:5.1f}  {tier}")
