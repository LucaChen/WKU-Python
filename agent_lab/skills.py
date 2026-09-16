from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError

from .tools import InventoryArgs, TotalArgs, inventory_tool, total_tool


class SkillError(BaseModel):
    ok: bool = False
    error: str
    hint: str = ""


class QuoteResult(BaseModel):
    ok: bool = True
    sku: str
    stock: int
    qty: int
    price: float
    total: float
    error: str = ""


def normalize_sku(raw: str) -> str:
    text = raw.strip().upper().replace(" ", "")
    aliases = {"小部件X": "WIDGET-X", "X型": "WIDGET-X", "迷你": "WIDGET-MINI"}
    for key, sku in aliases.items():
        if key.upper() in text or key in raw:
            return sku
    found = re.search(r"WIDGET-[A-Z]+", text)
    if found:
        return found.group(0)
    return text.replace("型", "")


def quote_skill(sku: str, qty: int, price: float, allow_repair: bool = True) -> Dict[str, Any]:
    """基础/进阶：库存查询 → Pydantic 清洗 → 金额计算。"""
    inv = inventory_tool.run(sku=sku)
    if not inv.ok and allow_repair:
        repaired = normalize_sku(sku)
        inv = inventory_tool.run(sku=repaired)
        sku = repaired
    if not inv.ok:
        return QuoteResult(ok=False, sku=sku, stock=0, qty=qty, price=price, total=0.0, error=inv.error).model_dump()
    tot = total_tool.run(qty=qty, price=price)
    if not tot.ok:
        return QuoteResult(ok=False, sku=inv.sku, stock=inv.stock, qty=qty, price=price, total=0.0, error=tot.error).model_dump()
    return QuoteResult(ok=True, sku=inv.sku, stock=inv.stock, qty=tot.qty, price=tot.price, total=tot.total).model_dump()


def self_correct_quote(user_text: str, qty: int = 2, price: float = 1299.0) -> Dict[str, Any]:
    """高难：模糊指令先失败，再根据错误自愈。"""
    first = quote_skill(user_text, qty, price, allow_repair=False)
    if first["ok"]:
        first["repaired"] = False
        first["attempts"] = 1
        return first
    second = quote_skill(normalize_sku(user_text), qty, price, allow_repair=True)
    second["repaired"] = True
    second["attempts"] = 2
    second["first_error"] = first["error"]
    return second
