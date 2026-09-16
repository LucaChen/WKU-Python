# 第08课-游戏市场综合分析

**主题**：游戏市场综合分析

**当堂验收**：Restart and Run All 能出清洗后行数、类型表、带口径的三句话结论。

**说明**：课堂讲义与本课数据同目录；课后练习使用题面指定的文件。从该文件夹启动内核。

课堂讲义与 `mobile_game_info.csv` 同目录；课后练习与 `googleplaystore.csv` 同目录。本班默认口径：去重留首次出现，只保留安卓。不要在遍历时删除元素。本课 CSV 可能带 UTF-8 BOM，打开课堂文件时使用 `encoding="utf-8-sig"`。
## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter08_游戏市场综合分析_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter08_游戏市场综合分析_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `mobile_game_info.csv` | 课堂数据，游戏记录 |
| `googleplaystore.csv` | 课后数据，50 条应用记录 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
