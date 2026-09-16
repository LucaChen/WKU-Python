"""第4课：条件判断与筛选。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "mobile_game_info.csv"


def load_body(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[1:]


def avg_of(rows, score_index=2):
    if not rows:
        return 0.0
    return sum(float(r[score_index]) for r in rows) / len(rows)


def main():
    print("=== 第4课 条件判断与筛选 ===")
    body = load_body(DATA)

    android = [r for r in body if r[6] == "TRUE"]
    not_android = [r for r in body if r[6] != "TRUE"]
    print("比较表达式示例:", body[0][6] == "TRUE")
    print("安卓行数:", len(android), "非安卓:", len(not_android))

    rpg = [r for r in body if r[3] == "角色扮演"]
    print("角色扮演平均分:", round(avg_of(rpg), 3))

    combo = [
        r
        for r in body
        if r[6] != "TRUE" and (r[3] == "角色扮演" or r[3] == "策略")
    ]
    print("非安卓且(角色扮演或策略) 行数:", len(combo), "平均分:", round(avg_of(combo), 3))

    high = mid = low = 0
    for row in body:
        score = float(row[2])
        if score >= 8.5:
            high += 1
        elif score >= 7.0:
            mid += 1
        else:
            low += 1
    print("高/中/低分:", high, mid, low, "合计:", high + mid + low)
    assert high + mid + low == len(body)
    print("本课验收通过")
    return len(combo), high + mid + low


if __name__ == "__main__":
    main()
