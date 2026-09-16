from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.skills import quote_skill, self_correct_quote  # noqa: E402


def main() -> None:
    print("=== 第18课 Skill 封装与链式联动（任务二 2.3 / 20分） ===")
    basic = quote_skill("WIDGET-X", qty=1, price=1299)
    print("基础 单工具命中:", basic)
    assert basic["ok"] and basic["sku"] == "WIDGET-X"

    chained = quote_skill("WIDGET-MINI", qty=2, price=699)
    print("进阶 双工具流转:", chained)
    assert chained["ok"] and chained["total"] == 1398.0

    repaired = self_correct_quote("帮我查一下小部件X的库存报价")
    print("高难 自愈:", repaired)
    assert repaired["ok"] and repaired["repaired"] is True and repaired["attempts"] == 2
    print("本课验收通过")


if __name__ == "__main__":
    main()
