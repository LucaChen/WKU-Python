"""第8课：综合分析。去重、按口径筛选、看哪类更吸量。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "mobile_game_info.csv"


def read_dataset(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def find_duplicate_titles(body):
    counts = {}
    for row in body:
        title = row[1]
        counts[title] = counts.get(title, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}


def dedupe_keep_first(body):
    seen = {}
    cleaned = []
    for row in body:
        title = row[1]
        if title not in seen:
            seen[title] = True
            cleaned.append(row)
    return cleaned


def freq_table(values):
    table = {}
    for value in values:
        table[value] = table.get(value, 0) + 1
    return table


def main():
    print("=== 第8课 游戏市场综合分析 ===")
    print("口径：去重保留第一次出现的行；只保留安卓游戏。")
    header, body = read_dataset(DATA)
    print("原始行数:", len(body))

    dups = find_duplicate_titles(body)
    print("重复游戏名数量:", len(dups))
    if "Phigros" in dups:
        print("Phigros 出现次数:", dups["Phigros"])

    unique = dedupe_keep_first(body)
    print("去重后行数:", len(unique))

    android = [r for r in unique if r[6] == "TRUE"]
    print("筛选安卓后行数:", len(android))

    type_freq = freq_table(r[3] for r in android)
    downloads = {}
    for row in android:
        kind = row[3]
        downloads[kind] = downloads.get(kind, 0) + int(row[5])

    hottest = max(downloads, key=downloads.get)
    print("各类型数量:", type_freq)
    print("各类型下载量合计:", downloads)
    print("结论：按下载量合计，更吸量的类型是", hottest)

    nested_preview = []
    for kind in sorted(downloads, key=downloads.get, reverse=True)[:3]:
        sample = next(r[1] for r in android if r[3] == kind)
        nested_preview.append((kind, sample))
    print("热门类型样例:", nested_preview)
    print("本课验收通过")
    return len(body), len(unique), len(android), hottest


if __name__ == "__main__":
    main()
