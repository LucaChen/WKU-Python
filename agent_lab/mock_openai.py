from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


class _Models:
    def __init__(self, parent: "FakeOpenAI"):
        self._parent = parent

    def list(self) -> Dict[str, Any]:
        return {"object": "list", "data": [{"id": mid, "object": "model"} for mid in self._parent.model_ids]}


class _Completions:
    def __init__(self, parent: "FakeOpenAI"):
        self._parent = parent

    def create(self, model: str, messages: List[Dict[str, str]], response_format: Optional[dict] = None, **kwargs: Any) -> Dict[str, Any]:
        text = self._parent.complete(messages, response_format=response_format, **kwargs)
        return {
            "id": "chatcmpl-lab",
            "object": "chat.completion",
            "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        }


class _Chat:
    def __init__(self, parent: "FakeOpenAI"):
        self.completions = _Completions(parent)


class FakeOpenAI:
    """OpenAI Chat Completions 形状的进程内端点。"""

    def __init__(self, model_ids: Optional[List[str]] = None):
        self.model_ids = model_ids or ["qwen2.5", "deepseek-r1"]
        self.base_url = "in-process://fake/v1"
        self.models = _Models(self)
        self.chat = _Chat(self)

    def complete(self, messages: List[Dict[str, str]], response_format: Optional[dict] = None, **kwargs: Any) -> str:
        blob = "\n".join(m.get("content", "") for m in messages)
        low = blob.lower()
        if "健康探活" in blob or "health" in low:
            return json.dumps({"ping": "ok", "serving": True}, ensure_ascii=False)
        if "用户信息" in blob or "user profile" in low:
            return json.dumps({"name": "张三", "phone": "13800138000", "age": 21}, ensure_ascii=False)
        if "工单" in blob:
            return json.dumps(
                {
                    "ticket_id": "T-10086",
                    "status": "open",
                    "items": [
                        {"sku": "WIDGET-X", "qty": 2, "price": 1299.0},
                        {"sku": "WIDGET-MINI", "qty": 1, "price": 699.0},
                    ],
                    "total": 3297.0,
                },
                ensure_ascii=False,
            )
        if "脏数据" in blob or "归一化" in blob:
            return json.dumps({"amount": "￥1,299.00", "currency": "CNY"}, ensure_ascii=False)
        if "inventory" in low or "库存" in blob:
            sku = "WIDGET-X"
            found = re.search(r"WIDGET-[A-Z]+", blob)
            if found:
                sku = found.group(0)
            stock = {"WIDGET-X": 12, "WIDGET-MINI": 4}.get(sku, 0)
            return json.dumps({"sku": sku, "stock": stock}, ensure_ascii=False)
        if "越界" in blob or "天气" in blob or "out of knowledge" in low:
            return json.dumps(
                {
                    "kind": "fallback",
                    "reason": "out_of_corpus",
                    "message": "知识库未覆盖该问题，拒绝编造答案。",
                    "question": blob[-80:],
                },
                ensure_ascii=False,
            )
        if "对比" in blob or "Widget-Mini" in blob:
            return json.dumps(
                {
                    "answer": "Widget-X 售价 1299 元、续航 48 小时；Widget-Mini 售价 699 元、续航 24 小时。",
                    "sources": [
                        {"chunk_id": "price::0", "confidence": 0.91, "quote": "Widget-X 官方售价 1299 元"},
                        {"chunk_id": "manual::0", "confidence": 0.88, "quote": "Widget-X 续航约 48 小时"},
                    ],
                },
                ensure_ascii=False,
            )
        if "续航" in blob:
            return json.dumps(
                {
                    "answer": "Widget-X 续航约 48 小时，充满约 2 小时。",
                    "sources": [{"chunk_id": "manual::0", "confidence": 0.93, "quote": "续航约 48 小时，充满电约 2 小时。"}],
                },
                ensure_ascii=False,
            )
        if response_format and response_format.get("type") == "json_object":
            return json.dumps({"ok": True, "echo": blob[-60:]}, ensure_ascii=False)
        return "收到。请提供更具体的任务。"


class HttpOpenAI:
    """极简 /v1 客户端，避免强依赖 openai 包。"""

    def __init__(self, base_url: str, api_key: str, timeout_s: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.models = self
        self.chat = self
        self.completions = self

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        url = self.base_url + path
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer %s" % self.api_key,
                "Content-Type": "application/json",
            },
        )
        with urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def list(self) -> dict:
        return self._request("GET", "/models")

    def create(self, **kwargs: Any) -> dict:
        return self._request("POST", "/chat/completions", kwargs)


def get_client(base_url: Optional[str] = None, api_key: str = "sk-local", timeout_s: float = 8.0):
    url = base_url or os.environ.get("OPENAI_BASE_URL")
    key = os.environ.get("OPENAI_API_KEY", api_key)
    if not url:
        return FakeOpenAI(), "fake"
    http = HttpOpenAI(url, key, timeout_s=timeout_s)
    try:
        http.list()
        return http, "http"
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return FakeOpenAI(), "fake-fallback"
