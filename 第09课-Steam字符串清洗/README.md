# 第09课-Steam字符串清洗

**主题**：Steam 字符串清洗

**当堂验收**：同一列清洗前后各 print 3 行；评价数转 int 成功计数。认不出列名的不能进入第 10 课。

**说明**：课堂讲义与本课数据同目录；课后练习使用题面指定的文件。从该文件夹启动内核。

课堂讲义与 `steam.csv` 同目录；课后练习使用 `steam_sample.csv`。不要沿用移动游戏表的列下标。同目录 `mobile_game_info.csv` 仅作对照。打开 CSV 使用 `encoding="utf-8-sig"`。不要把 2.7 万行整表打印出来。
## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter09_Steam字符串清洗_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter09_Steam字符串清洗_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `steam.csv` | 课堂数据，约 2.7 万行 Steam 记录；演示只打印 header 与两行样例 |
| `steam_sample.csv` | 课后数据，表头 + 前 50 条记录 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
