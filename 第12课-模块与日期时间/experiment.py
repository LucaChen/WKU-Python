"""第12课：datetime 统一新冠县日数据的日期。"""

from datetime import datetime
from pathlib import Path
import csv


DATA = Path(__file__).resolve().parent / "covid_sample.csv"


def main():
    print("=== 第12课 模块与日期时间 ===")
    print("本班锁定写法: from datetime import datetime")

    with DATA.open(newline="", encoding="utf-8-sig") as handle:
        body = list(csv.DictReader(handle))
    print("样本行数:", len(body))

    parsed = []
    for row in body:
        parsed.append(datetime.strptime(row["date"], "%Y-%m-%d"))

    try:
        datetime.strptime(body[0]["date"], "%d/%m/%Y")
    except ValueError:
        print("格式串与数据不一致会 ValueError（预期）")

    unified = [dt.strftime("%Y/%m/%d") for dt in parsed]
    print("统一格式前5行:", unified[:5])

    earliest = min(parsed)
    latest = max(parsed)
    span = latest - earliest
    print("最早:", earliest.date(), "最晚:", latest.date(), "跨度天数:", span.days)
    print("本课验收通过")
    return earliest, latest, span.days


if __name__ == "__main__":
    main()
