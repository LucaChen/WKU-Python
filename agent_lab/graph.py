from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional

START = "__start__"
END = "__end__"


def add_messages(old: Optional[List], new: Optional[List]) -> List:
    return list(old or []) + list(new or [])


def overwrite(_old: Any, new: Any) -> Any:
    return new


class MemorySaver:
    def __init__(self) -> None:
        self.store: Dict[str, dict] = {}

    def put(self, thread_id: str, state: dict) -> None:
        self.store[thread_id] = deepcopy(state)

    def get(self, thread_id: str) -> Optional[dict]:
        data = self.store.get(thread_id)
        return deepcopy(data) if data is not None else None


class CompiledGraph:
    def __init__(self, graph: "StateGraph", checkpointer: Optional[MemorySaver], recursion_limit: int):
        self.graph = graph
        self.checkpointer = checkpointer or MemorySaver()
        self.recursion_limit = recursion_limit

    def invoke(self, state: dict, config: Optional[dict] = None) -> dict:
        thread_id = (config or {}).get("configurable", {}).get("thread_id", "default")
        saved = self.checkpointer.get(thread_id)
        current = self.graph.merge_state(saved or {}, state)
        node = self.graph.entry
        steps = 0
        trace = list(current.get("trace") or [])
        while node not in (None, END):
            steps += 1
            if steps > self.recursion_limit:
                raise RuntimeError("recursion_limit=%s 已触发熔断" % self.recursion_limit)
            fn = self.graph.nodes[node]
            update = fn(current) or {}
            current = self.graph.merge_state(current, update)
            trace.append({"step": steps, "node": node, "keys": sorted(update.keys())})
            current["trace"] = trace
            node = self.graph.next_node(node, current)
        self.checkpointer.put(thread_id, current)
        return current


class StateGraph:
    """教学用 StateGraph：接口对齐 LangGraph 的 Node / Edge / 条件边。"""

    def __init__(self, channels: Optional[Dict[str, Callable]] = None):
        self.channels = channels or {"messages": add_messages, "trace": add_messages}
        self.nodes: Dict[str, Callable[[dict], dict]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional: Dict[str, tuple] = {}
        self.entry = START

    def add_node(self, name: str, fn: Callable[[dict], dict]) -> "StateGraph":
        self.nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        if source == START:
            self.entry = target
        self.edges[source] = target
        return self

    def add_conditional_edges(self, source: str, router: Callable[[dict], str], mapping: Dict[str, str]) -> "StateGraph":
        self.conditional[source] = (router, mapping)
        return self

    def merge_state(self, old: dict, new: dict) -> dict:
        merged = dict(old)
        for key, value in new.items():
            reducer = self.channels.get(key, overwrite)
            merged[key] = reducer(old.get(key), value)
        return merged

    def next_node(self, source: str, state: dict) -> str:
        if source in self.conditional:
            router, mapping = self.conditional[source]
            label = router(state)
            return mapping[label]
        return self.edges.get(source, END)

    def compile(self, checkpointer: Optional[MemorySaver] = None, recursion_limit: int = 8) -> CompiledGraph:
        return CompiledGraph(self, checkpointer, recursion_limit)
