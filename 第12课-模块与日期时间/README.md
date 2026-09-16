# 第12课-模块与日期时间

**主题**：模块与日期时间

**当堂验收**：统一日期格式 5 行 + 一个时间差。

**说明**：课堂讲义与本课数据同目录；课后练习使用题面指定的文件。从该文件夹启动内核。

只用 `covid_sample.csv`，不要读 80 万行全表。本课 CSV 可能带 UTF-8 BOM，使用 `encoding="utf-8-sig"`。全班锁定 `from datetime import datetime`。最早最晚与跨度天数由学生代码计算。
## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter12_模块与日期时间_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter12_模块与日期时间_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `covid_sample.csv` | 课堂与课后数据，华盛顿州抽样 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
