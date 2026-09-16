from __future__ import annotations

import re
from typing import List, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class UserProfile(BaseModel):
    """基础：单层扁平字段。"""

    name: str = Field(min_length=1, description="姓名")
    phone: str = Field(description="11 位大陆手机号")
    age: int = Field(ge=0, le=120)

    @field_validator("phone")
    @classmethod
    def phone_cn(cls, value: str) -> str:
        text = re.sub(r"\s+", "", value)
        if not re.fullmatch(r"1\d{10}", text):
            raise ValueError("手机号必须是 1 开头的 11 位数字")
        return text


class LineItem(BaseModel):
    sku: str
    qty: int = Field(gt=0)
    price: float = Field(ge=0)


class TicketAnalysis(BaseModel):
    """进阶：多层嵌套 + 枚举 + 合计。"""

    ticket_id: str
    status: Literal["open", "pending", "closed"]
    items: List[LineItem]
    total: float = Field(ge=0)

    @model_validator(mode="after")
    def total_matches(self) -> "TicketAnalysis":
        expected = round(sum(item.qty * item.price for item in self.items), 2)
        if round(self.total, 2) != expected:
            raise ValueError("total=%s 与明细合计 %s 不一致" % (self.total, expected))
        return self


class DirtyAmount(BaseModel):
    """高难：自定义校验器做脏数据归一化，无法归一则拦截。"""

    amount: float = Field(description="归一化后的金额")
    currency: str = "CNY"

    @field_validator("amount", mode="before")
    @classmethod
    def normalize_amount(cls, value):
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().replace("￥", "").replace("¥", "").replace(",", "").replace("元", "")
        text = text.replace(" ", "")
        if not re.fullmatch(r"-?\d+(\.\d+)?", text):
            raise ValueError("无法从 %r 解析金额" % value)
        return float(text)


def parse_model(model, payload):
    try:
        return True, model.model_validate(payload)
    except ValidationError as exc:
        return False, exc
