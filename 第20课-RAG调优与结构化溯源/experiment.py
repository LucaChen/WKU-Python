from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "agent_lab" / "knowledge"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.rag import Retriever, answer_with_rag, load_corpus  # noqa: E402


def main() -> None:
    print("=== 第20课 RAG 调优与结构化溯源（任务三 3.2 / 25分） ===")
    retriever = Retriever(load_corpus(KB))

    basic = answer_with_rag(retriever, "Widget-X 续航多久？")
    print("基础 单文档:", basic["kind"], basic.get("sources", [{}])[0].get("chunk_id"))
    assert basic["kind"] == "answer" and basic["sources"]

    advanced = answer_with_rag(retriever, "对比 Widget-X 和 Widget-Mini 的价格与续航")
    print("进阶 跨文档:", [s["chunk_id"] for s in advanced.get("sources", [])])
    assert advanced["kind"] == "answer"
    docs = {s["chunk_id"].split("::")[0] for s in advanced["sources"]}
    assert len(docs) >= 2

    hard = answer_with_rag(retriever, "明天深圳天气怎么样？")
    print("高难 越界兜底:", hard)
    assert hard["kind"] == "fallback" and hard["reason"] == "out_of_corpus"
    print("本课验收通过")


if __name__ == "__main__":
    main()
