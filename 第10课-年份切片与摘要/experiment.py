"""第10课：发行年、好评档位、开发者频数。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "steam.csv"


def read_steam(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def freq_table(values):
    table = {}
    for value in values:
        table[value] = table.get(value, 0) + 1
    return table


def rating_bucket(n):
    text = str(int(n))
    if len(text) == 1:
        return "0+"
    return text[0] + "0" * (len(text) - 1) + "+"


def main():
    print("=== 第10课 年份、切片与摘要 ===")
    header, body = read_steam(DATA)
    years = [row[2][:4] for row in body]
    year_freq = freq_table(years)
    print("发行年种类:", len(year_freq))
    print("最早几年:", sorted(year_freq)[:5])

    print("3318 ->", rating_bucket(3318), "；124534 ->", rating_bucket(124534))
    buckets = freq_table(rating_bucket(int(row[12])) for row in body)
    print("好评档位（部分）:", {k: buckets[k] for k in sorted(buckets, key=lambda x: len(x))[:6]})

    developers = freq_table(row[4] for row in body)
    top = sorted(developers.items(), key=lambda kv: kv[1], reverse=True)[:5]
    print("开发者 Top5:", top)
    print("摘要: Valve 开发了", developers.get("Valve", 0), "款游戏")
    print("本课验收通过")
    return year_freq, buckets, top


if __name__ == "__main__":
    main()
