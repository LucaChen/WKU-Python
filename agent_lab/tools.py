from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

from pydantic import BaseModel, Field, ValidationError


class InventoryArgs(BaseModel):
    sku: str = Field(min_length=3, description="商品 SKU，例如 WIDGET-X")


class InventoryResult(BaseModel):
    sku: str
    stock: int
    ok: bool = True
    error: str = ""


class TotalArgs(BaseModel):
    qty: int = Field(gt=0)
    price: float = Field(ge=0)


class TotalResult(BaseModel):
    qty: int
    price: float
    total: float
    ok: bool = True
    error: str = ""


STOCK = {"WIDGET-X": 12, "WIDGET-MINI": 4}


class Tool:
    def __init__(self, name: str, description: str, args_schema: Type[BaseModel], result_schema: Type[BaseModel], fn: Callable):
        self.name = name
        self.description = description
        self.args_schema = args_schema
        self.result_schema = result_schema
        self.fn = fn

    def export_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }

    def run(self, **kwargs: Any) -> BaseModel:
        try:
            args = self.args_schema.model_validate(kwargs)
            raw = self.fn(args)
            return self.result_schema.model_validate(raw)
        except ValidationError as exc:
            return self.result_schema.model_validate(
                {"ok": False, "error": "参数校验失败: %s" % exc.errors()[0]["msg"], **self._empty_result()}
            )
        except Exception as exc:  # noqa: BLE001
            return self.result_schema.model_validate(
                {"ok": False, "error": "执行隔离: %s" % exc, **self._empty_result()}
            )

    def _empty_result(self) -> dict:
        if self.result_schema is InventoryResult:
            return {"sku": "", "stock": 0}
        if self.result_schema is TotalResult:
            return {"qty": 0, "price": 0.0, "total": 0.0}
        return {}


def lookup_inventory(args: InventoryArgs) -> dict:
    sku = args.sku.upper().replace(" ", "")
    if sku not in STOCK:
        return {"sku": sku, "stock": 0, "ok": False, "error": "未知 SKU"}
    return {"sku": sku, "stock": STOCK[sku], "ok": True, "error": ""}


def calc_total(args: TotalArgs) -> dict:
    return {"qty": args.qty, "price": args.price, "total": round(args.qty * args.price, 2), "ok": True, "error": ""}


inventory_tool = Tool(
    "inventory_lookup",
    "按 SKU 查询库存",
    InventoryArgs,
    InventoryResult,
    lookup_inventory,
)
total_tool = Tool(
    "calc_total",
    "按数量与单价计算金额",
    TotalArgs,
    TotalResult,
    calc_total,
)


def registry() -> Dict[str, Tool]:
    return {inventory_tool.name: inventory_tool, total_tool.name: total_tool}
