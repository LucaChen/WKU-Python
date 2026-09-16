from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "agent_lab" / "knowledge"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.rag import Retriever, load_corpus  # noqa: E402
from agent_lab.tools import Tool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


class SearchArgs(BaseModel):
    query: str = Field(min_length=2)


class SearchResult(BaseModel):
    ok: bool = True
    error: str = ""
    hits: list = Field(default_factory=list)


def main() -> None:
    print("=== 第19课 RAG 检索流水线（任务三 3.1 / 15分） ===")
    chunks = load_corpus(KB)
    print("分块数:", len(chunks), "来自", [c.doc_id for c in chunks[:3]])
    retriever = Retriever(chunks)

    def _search(args: SearchArgs):
        hits = retriever.search(args.query, k=3)
        return {"ok": True, "error": "", "hits": [h.model_dump() for h in hits]}

    rag_tool = Tool("rag_search", "从产品知识库检索", SearchArgs, SearchResult, _search)
    result = rag_tool.run(query="Widget-X 续航")
    print("Retriever 作为 Tool:", result.ok, result.hits[0]["chunk_id"] if result.hits else None)
    assert result.ok and result.hits
    assert any("续航" in h["text"] or "48" in h["text"] for h in result.hits)
    print("命中文本:", result.hits[0]["text"][:40])
    print("本课验收通过")


if __name__ == "__main__":
    main()
