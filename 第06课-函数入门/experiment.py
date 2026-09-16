"""第6课：函数入门。抽列 + 频数 + 函数调函数。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "mobile_game_info.csv"


def load_body(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[1:]


def square(n):
    return n * n


def extract_column(table, index):
    column = []
    for row in table:
        column.append(row[index])
    return column


def freq_table(values):
    table = {}
    for value in values:
        if value not in table:
            table[value] = 0
        table[value] += 1
    return table


def column_freq(table, index):
    return freq_table(extract_column(table, index))


def main():
    print("=== 第6课 函数入门 ===")
    print("square(5) =", square(5))
    body = load_body(DATA)
    titles = extract_column(body, 1)
    scores = extract_column(body, 2)
    print("名字列前3:", titles[:3])
    print("评分列前3:", scores[:3])
    type_freq = column_freq(body, 3)
    print("类型频率:", type_freq)
    print("本课验收通过")
    return type_freq


if __name__ == "__main__":
    main()
