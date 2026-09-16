from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str


class Hit(BaseModel):
    chunk_id: str
    score: float
    text: str
    doc_id: str


class SourcedAnswer(BaseModel):
    answer: str
    sources: List[dict] = Field(default_factory=list)
    kind: str = "answer"


class FallbackResponse(BaseModel):
    kind: str = "fallback"
    reason: str
    message: str
    question: str


def tokenize(text: str) -> List[str]:
    text = text.lower()
    latin = re.findall(r"[a-z0-9]+", text)
    blocks = re.findall(r"[\u4e00-\u9fff]+", text)
    grams: List[str] = []
    for span in blocks:
        grams.append(span)
        for i in range(len(span)):
            grams.append(span[i])
            if i + 1 < len(span):
                grams.append(span[i : i + 2])
    return latin + grams


def chunk_text(doc_id: str, text: str, size: int = 80) -> List[Chunk]:
    parts = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks = []
    buf = ""
    idx = 0
    for part in parts:
        if len(buf) + len(part) > size and buf:
            chunks.append(Chunk(chunk_id="%s::%s" % (doc_id, idx), doc_id=doc_id, text=buf))
            idx += 1
            buf = part
        else:
            buf = (buf + " " + part).strip()
    if buf:
        chunks.append(Chunk(chunk_id="%s::%s" % (doc_id, idx), doc_id=doc_id, text=buf))
    return chunks


def _tf(tokens: List[str]) -> Counter:
    return Counter(tokens)


def cosine(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def bm25(query: Counter, doc: Counter, avgdl: float, k1: float = 1.2, b: float = 0.75) -> float:
    dl = sum(doc.values()) or 1
    score = 0.0
    for term, qf in query.items():
        f = doc.get(term, 0)
        if f == 0:
            continue
        idf = math.log(1 + 1.5)
        score += idf * qf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
    return score


class Retriever:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.vecs = [_tf(tokenize(c.text)) for c in chunks]
        self.avgdl = sum(sum(v.values()) for v in self.vecs) / max(len(self.vecs), 1)

    def search(self, query: str, k: int = 3, hybrid: bool = True) -> List[Hit]:
        q = _tf(tokenize(query))
        ranked: List[Tuple[float, Chunk]] = []
        for chunk, vec in zip(self.chunks, self.vecs):
            v = cosine(q, vec)
            b = bm25(q, vec, self.avgdl)
            score = 0.6 * v + 0.4 * b if hybrid else v
            ranked.append((score, chunk))
        ranked.sort(key=lambda x: x[0], reverse=True)
        reranked = ranked[: max(k * 2, k)]
        hits = [
            Hit(chunk_id=c.chunk_id, score=round(s, 4), text=c.text, doc_id=c.doc_id)
            for s, c in reranked[:k]
        ]
        return hits


OUT_OF_CORPUS = ("天气", "股价", "中奖", "彩票", "总统")


def load_corpus(folder: Path) -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in sorted(folder.glob("*.md")):
        chunks.extend(chunk_text(path.stem, path.read_text(encoding="utf-8")))
    return chunks


def answer_with_rag(retriever: Retriever, question: str) -> dict:
    if any(key in question for key in OUT_OF_CORPUS):
        return FallbackResponse(
            reason="out_of_corpus",
            message="知识库未覆盖该问题，拒绝编造答案。",
            question=question,
        ).model_dump()
    hits = retriever.search(question, k=3, hybrid=True)
    if not hits or hits[0].score < 0.05:
        return FallbackResponse(
            reason="low_confidence",
            message="检索置信过低，返回兜底而非幻觉。",
            question=question,
        ).model_dump()
    quotes = [{"chunk_id": h.chunk_id, "confidence": h.score, "quote": h.text[:80]} for h in hits]
    answer = " ".join(h.text for h in hits[:2])
    return SourcedAnswer(answer=answer, sources=quotes).model_dump()
