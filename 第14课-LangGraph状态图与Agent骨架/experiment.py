from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.graph import END, START, MemorySaver, StateGraph, add_messages  # noqa: E402


def main() -> None:
    print("=== 第14课 LangGraph 状态图与 Agent 骨架 ===")
    channels = {"messages": add_messages, "trace": add_messages, "need_tool": lambda _o, n: n, "result": lambda _o, n: n}

    def agent(state):
        text = state.get("user", "")
        need = "库存" in text or "sku" in text.lower()
        return {"messages": ["think:" + text], "need_tool": need}

    def tool_node(state):
        return {"messages": ["tool:stock=12"], "result": "WIDGET-X=12"}

    def finalize(state):
        return {"messages": ["final:" + str(state.get("result") or "no-tool")]}

    def route(state):
        return "tool" if state.get("need_tool") else "end"

    graph = StateGraph(channels)
    graph.add_node("agent", agent)
    graph.add_node("tool", tool_node)
    graph.add_node("finalize", finalize)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route, {"tool": "tool", "end": "finalize"})
    graph.add_edge("tool", "finalize")
    graph.add_edge("finalize", END)
    saver = MemorySaver()
    app = graph.compile(checkpointer=saver, recursion_limit=8)
    r1 = app.invoke({"user": "查询 WIDGET-X 库存", "messages": []}, {"configurable": {"thread_id": "u1"}})
    r2 = app.invoke({"user": "只是打个招呼", "messages": []}, {"configurable": {"thread_id": "u1"}})
    print("首轮节点轨迹:", [t["node"] for t in r1["trace"]])
    print("次轮轨迹:", [t["node"] for t in r2["trace"]])
    print("messages 经 reducer 累积:", r2["messages"])
    assert r1["trace"][0]["node"] == "agent"
    assert "tool" in [t["node"] for t in r1["trace"]]
    try:
        boom = StateGraph(channels)
        boom.add_node("loop", lambda s: {"messages": ["x"]})
        boom.add_edge(START, "loop")
        boom.add_edge("loop", "loop")
        boom.compile(recursion_limit=3).invoke({"messages": []})
        raise AssertionError("应当熔断")
    except RuntimeError as exc:
        print("熔断:", exc)
    print("本课验收通过")
    return r1, r2


if __name__ == "__main__":
    main()
