# 一次性生成各课 README / 实验说明 / notebook
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

META = [
    ("第01课-环境与第一次计算", "环境与第一次计算", "能新建或运行代码，print(2+9) 有输出。", "原讲义 experiment1.ipynb 是练习册；experiment.py 是验收版。"),
    ("第02课-变量类型与字符串", "变量、类型与字符串", "赋值覆盖、int(3.9)、字符串拼接、读懂 TypeError。", "experiment2-1 至 2-9 是分任务讲义，格子留给学生填。"),
    ("第03课-列表文件与循环", "列表、文件与循环", "读 csv，len(body) 与全表平均分。", "必须先确认 mobile_game_info.csv 与 notebook 同目录。"),
    ("第04课-条件判断与筛选", "条件判断与筛选", "组合条件平均分 + 高中低分计数守恒。", "isAndroid 在文件里是字符串 TRUE/FALSE。"),
    ("第05课-字典与频数", "字典与频数", "类型频率字典 + 百分比。", "四步：空字典 → 循环 → 键不在则 0 → +1。"),
    ("第06课-函数入门", "函数入门", "抽列函数 + 频数函数，函数调函数。", "不要重写第5课逻辑，把它缩进到 def 里。"),
    ("第07课-函数进阶", "函数进阶", "默认参数、拆包元组、分清局部/全局。", "破坏性实验会临时覆盖 print，跑完即恢复。"),
    ("第08课-游戏市场综合分析", "游戏市场综合分析", "去重、筛安卓、回答哪类更吸量。", "口径写在输出第一句：去重留首次出现，只保留安卓。"),
    ("第09课-Steam字符串清洗", "Steam 字符串清洗", "认列、replace、平台统一、评价数转 int。", "不要沿用移动游戏表的列下标。"),
    ("第10课-年份切片与摘要", "年份、切片与摘要", "四位年频率 + 100000+ 档 + 开发者 Top。", "档位规则：取首位，其余补 0，再加号。"),
    ("第11课-贪吃蛇与面向对象", "贪吃蛇与面向对象", "能动、能吃 1 次、能撞墙死。", "游玩：python3 snake.py；验收：python3 snake.py --demo"),
    ("第12课-模块与日期时间", "模块与日期时间", "统一日期格式 5 行 + 一个时间差。", "只用 covid_sample.csv，不要读 80 万行全表。"),
]


def write_readme(folder, title, accept, note):
    text = f"""# {folder}

**主题**：{title}

**当堂验收**：{accept}

**说明**：{note}

## 本课文件

运行验收版：

```bash
python3 experiment.py
```
"""
    if folder.startswith("第11"):
        text += """
键盘游玩：

```bash
python3 snake.py
```
"""
    (ROOT / folder / "README.md").write_text(text, encoding="utf-8")


def write_intro(folder, title, accept):
    text = f"""# 实验说明 · {title}

你将创造什么：完成本课实验后，应能做到——{accept}

运行方法：在本文件夹执行 `python3 experiment.py`（第 11 课游玩用 `python3 snake.py`）。

更完整的学生叙事见仓库根目录 `实验内容介绍.md`，课堂时间盒见本课 `教案.md`。
"""
    (ROOT / folder / "实验说明.md").write_text(text, encoding="utf-8")


def py_to_notebook(py_path: Path, title: str) -> dict:
    code = py_path.read_text(encoding="utf-8")
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title}\n", "\n", "下面是本课验收版代码，可整本运行。\n"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in code.splitlines()],
            },
        ],
    }


def main():
    for folder, title, accept, note in META:
        write_readme(folder, title, accept, note)
        write_intro(folder, title, accept)
        py_path = ROOT / folder / "experiment.py"
        nb_path = ROOT / folder / "experiment.ipynb"
        nb_path.write_text(
            json.dumps(py_to_notebook(py_path, title), ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    print("docs ok")


if __name__ == "__main__":
    main()
