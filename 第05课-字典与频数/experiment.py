"""第5课：字典与频数。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "mobile_game_info.csv"


def load_body(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[1:]


def freq_table(values):
    table = {}
    for value in values:
        if value not in table:
            table[value] = 0
        table[value] = table[value] + 1
    return table


def main():
    print("=== 第5课 字典与频数 ===")
    body = load_body(DATA)
    types = [row[3] for row in body]
    table = freq_table(types)
    print("类型频数:", table)

    demo = {"角色扮演": 67}
    try:
        print(demo["不存在"])
    except KeyError:
        print("访问不存在的键会 KeyError（预期），用 in 先判断")

    total = sum(table.values())
    percent = {k: round(v / total * 100, 2) for k, v in table.items()}
    print("百分比:", percent)
    print("百分比合计:", round(sum(percent.values()), 2))
    print("本课验收通过")
    return table


if __name__ == "__main__":
    main()
