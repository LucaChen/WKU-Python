# 第07课-函数进阶

**主题**：函数进阶

**当堂验收**：拆包两个返回值；能说明函数内赋值没有改掉外部变量。

**说明**：课堂讲义与本课数据同目录；课后练习使用题面指定的文件。从该文件夹启动内核。

课堂讲义与 `mobile_game_info.csv` 同目录；课后练习与 `googleplaystore.csv` 同目录。破坏性实验会临时覆盖 `print`，同一格必须先保存内置名并在结束时恢复。不要使用 `global`。本课 CSV 可能带 UTF-8 BOM，打开课堂文件时使用 `encoding="utf-8-sig"`。
## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter07_函数进阶_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter07_函数进阶_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `mobile_game_info.csv` | 课堂数据，游戏记录 |
| `googleplaystore.csv` | 课后数据，50 条应用记录 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
