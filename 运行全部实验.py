"""在各课文件夹中依次运行 experiment.py，汇总是否通过。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LESSONS = [
    "第01课-环境与第一次计算",
    "第02课-变量类型与字符串",
    "第03课-列表文件与循环",
    "第04课-条件判断与筛选",
    "第05课-字典与频数",
    "第06课-函数入门",
    "第07课-函数进阶",
    "第08课-游戏市场综合分析",
    "第09课-Steam字符串清洗",
    "第10课-年份切片与摘要",
    "第11课-贪吃蛇与面向对象",
    "第12课-模块与日期时间",
    "第13课-模型私有化部署与Serving",
    "第14课-LangGraph状态图与Agent骨架",
    "第15课-OpenClaw运行时初始化",
    "第16课-Pydantic结构化Prompt",
    "第17课-自定义Tool与MCP接入",
    "第18课-Skill封装与链式联动",
    "第19课-RAG检索流水线",
    "第20课-RAG调优与结构化溯源",
]


def run_one(name: str) -> tuple[bool, str]:
    folder = ROOT / name
    script = folder / "experiment.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(folder),
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    ok = result.returncode == 0 and "本课验收通过" in output
    return ok, output


def main():
    rows = []
    for name in LESSONS:
        ok, output = run_one(name)
        status = "通过" if ok else "失败"
        print(f"[{status}] {name}")
        if not ok:
            print(output)
        rows.append((name, ok, output))
    passed = sum(1 for _, ok, _ in rows if ok)
    print(f"\n合计 {passed}/{len(rows)} 通过")
    if passed != len(rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
