from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .mock_openai import get_client


class HealthReport(BaseModel):
    ok: bool
    base_url: str
    model_ids: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    json_ok: bool = False
    detail: str = ""
    source: str = "fake"


class ProbePayload(BaseModel):
    ping: str = "ok"
    serving: bool = True


def probe(base_url: Optional[str] = None, api_key: str = "sk-local", timeout_s: float = 8.0) -> HealthReport:
    import json
    import time

    client, source = get_client(base_url=base_url, api_key=api_key, timeout_s=timeout_s)
    t0 = time.time()
    models = client.models.list()
    latency = (time.time() - t0) * 1000
    ids = [m["id"] for m in models.get("data", [])]
    completion = client.chat.completions.create(
        model=ids[0] if ids else "qwen2.5",
        messages=[
            {
                "role": "system",
                "content": "只输出 JSON。字段 ping=ok, serving=true。",
            },
            {"role": "user", "content": "健康探活"},
        ],
        response_format={"type": "json_object"},
    )
    raw = completion["choices"][0]["message"]["content"]
    json_ok = False
    detail = raw
    try:
        parsed = ProbePayload.model_validate(json.loads(raw))
        json_ok = parsed.ping == "ok" and parsed.serving is True
        detail = parsed.model_dump_json()
    except Exception as exc:  # noqa: BLE001 — 探活必须隔离异常
        detail = "JSON 约束失败: %s | raw=%s" % (exc, raw)
    ok = bool(ids) and json_ok
    return HealthReport(
        ok=ok,
        base_url=getattr(client, "base_url", base_url or "in-process://fake"),
        model_ids=ids,
        latency_ms=round(latency, 2),
        json_ok=json_ok,
        detail=detail,
        source=source,
    )
