from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .graph import END, START, MemorySaver, StateGraph, add_messages
from .health import HealthReport, probe
from .mock_openai import get_client


class OpenClawConfig(BaseModel):
    """把 LangGraph 运行时配置映射到 OpenClaw Client。"""

    base_url: Optional[str] = Field(default=None, description="私有化 /v1 端点，空则用教学 Fake")
    api_key: str = "sk-local"
    timeout_s: float = 8.0
    model: str = "qwen2.5"
    agent_runtime: str = "openclaw"
    session_id: str = "lab-session"


class StateTransition(BaseModel):
    turn: int
    node: str
    message: str
    runtime: str


class OpenClawClient:
    def __init__(self, config: Optional[OpenClawConfig] = None):
        self.config = config or OpenClawConfig()
        self.client, self.source = get_client(
            self.config.base_url, self.config.api_key, self.config.timeout_s
        )
        self.saver = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        channels = {"messages": add_messages, "trace": add_messages, "reply": lambda _o, n: n}

        def agent_node(state: dict) -> dict:
            user = state.get("user", "")
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": user or "握手"}],
            )
            reply = completion["choices"][0]["message"]["content"]
            return {"messages": ["agent:" + reply[:80]], "reply": reply}

        graph = StateGraph(channels)
        graph.add_node("agent", agent_node)
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)
        return graph.compile(checkpointer=self.saver, recursion_limit=6)

    def handshake(self) -> HealthReport:
        return probe(self.config.base_url, self.config.api_key, self.config.timeout_s)

    def run_turn(self, user_text: str, thread_id: Optional[str] = None) -> dict:
        tid = thread_id or self.config.session_id
        result = self.graph.invoke({"user": user_text, "messages": ["user:" + user_text]}, {"configurable": {"thread_id": tid}})
        log = [
            StateTransition(
                turn=i + 1,
                node=item["node"],
                message=user_text,
                runtime=self.config.agent_runtime,
            ).model_dump()
            for i, item in enumerate(result.get("trace") or [])
        ]
        result["state_log"] = log
        result["source"] = self.source
        result["thread_id"] = tid
        return result
