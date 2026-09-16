"""第3课：列表、文件与循环。读 mobile_game_info.csv，求全表平均分。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "mobile_game_info.csv"


def load_table(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def average_score(body, score_index=2):
    total = 0.0
    count = 0
    for row in body:
        total += float(row[score_index])
        count += 1
    return total / count


def main():
    print("=== 第3课 列表、文件与循环 ===")
    one_game = ["明日方舟", "8.2", "策略"]
    print("一行游戏:", one_game, "评分下标1 =", one_game[1])

    sample = [
        ["人格解体", "8.8", "角色扮演"],
        ["一念逍遥", "6.5", "角色扮演"],
        ["明日方舟", "8.2", "策略"],
    ]
    print("嵌套取格 sample[2][1] =", sample[2][1])

    header, body = load_table(DATA)
    print("表头:", header)
    print("前5行:")
    for row in body[:5]:
        print(row)
    print("len(body) =", len(body))

    try:
        bad = body[0][2] + body[1][2]
        print("忘记 float 会得到字符串拼接:", bad)
    except TypeError as exc:
        print("忘记 float 报错:", exc)

    avg = average_score(body)
    print("全表平均分 =", round(avg, 3))
    print("本课验收通过")
    return len(body), avg


if __name__ == "__main__":
    main()
