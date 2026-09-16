from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.schemas import DirtyAmount, TicketAnalysis, UserProfile, parse_model  # noqa: E402


def main() -> None:
    print("=== 第16课 Pydantic 结构化 Prompt（任务一 1.2 / 15分） ===")
    ok, profile = parse_model(UserProfile, {"name": "张三", "phone": "138 0013 8000", "age": 21})
    print("基础用例 扁平用户:", ok, profile)
    assert ok and profile.phone == "13800138000"

    ok, ticket = parse_model(
        TicketAnalysis,
        {
            "ticket_id": "T-10086",
            "status": "open",
            "items": [
                {"sku": "WIDGET-X", "qty": 2, "price": 1299.0},
                {"sku": "WIDGET-MINI", "qty": 1, "price": 699.0},
            ],
            "total": 3297.0,
        },
    )
    print("进阶用例 嵌套工单:", ok, ticket.total if ok else ticket)
    assert ok

    ok, dirty = parse_model(DirtyAmount, {"amount": "￥1,299.00", "currency": "CNY"})
    print("高难用例 金额归一:", ok, dirty)
    assert ok and dirty.amount == 1299.0
    bad_ok, bad = parse_model(DirtyAmount, {"amount": "免费送", "currency": "CNY"})
    print("对抗拦截:", bad_ok, str(bad.errors()[0]["msg"])[:40] if not bad_ok else bad)
    assert not bad_ok
    print("本课验收通过")


if __name__ == "__main__":
    main()
