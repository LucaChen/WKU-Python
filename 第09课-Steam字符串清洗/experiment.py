"""第9课：Steam 字符串清洗。"""

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "steam.csv"


def read_steam(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def clean_platforms(text):
    parts = [p.strip().capitalize() for p in text.replace(";", " ").split() if p.strip()]
    return ";".join(parts)


def parse_owners(text):
    cleaned = text.replace(",", "").replace(" ", "")
    if "-" in cleaned:
        low, high = cleaned.split("-", 1)
        return int(low), int(high)
    return int(cleaned), int(cleaned)


def main():
    print("=== 第9课 Steam 字符串清洗 ===")
    header, body = read_steam(DATA)
    print("列名:", header)
    print("样例两行:")
    for row in body[:2]:
        print(row[1], row[6], row[12], row[16])

    dirty = "Action; FPS ;action"
    print("replace 清洗分类:", dirty.replace(" ", "").replace("action", "Action"))

    before = body[0][6]
    after = clean_platforms(before)
    print("平台清洗:", before, "->", after)

    converted = 0
    failed = 0
    for row in body:
        try:
            int(row[12])
            converted += 1
        except ValueError:
            failed += 1
    print("评价数转 int 成功:", converted, "失败:", failed)

    try:
        int("12,4534")
    except ValueError:
        print("未清洗就 int('12,4534') 会 ValueError（预期）")

    owners_demo = parse_owners(body[0][16])
    print("owners 解析", body[0][16], "->", owners_demo)
    print("本课验收通过")
    return converted, owners_demo


if __name__ == "__main__":
    main()
