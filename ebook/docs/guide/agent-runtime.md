---
title: agent_lab 运行时
outline: deep
---

# agent_lab · Agent 实训教学运行时

本目录给第 13–20 课共用。课堂验收**不要求 GPU**，也不强制安装 `langgraph` / `openai`。

未设置 `OPENAI_BASE_URL` 时，使用进程内 `FakeOpenAI`（接口形状对齐 OpenAI Chat Completions `/v1`）。若本机已用 Ollama 或 vLLM 起了兼容端点，可：

```bash
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="sk-local"
python3 第13课-模型私有化部署与Serving/experiment.py
```

真实端点不可达时会回退到 Fake，保证 `experiment.py` 可重复通过。

| 模块 | 对应课次 |
|------|----------|
| `health.py` / `mock_openai.py` | 第 13 课 Serving 探活 |
| `graph.py` | 第 14 课 StateGraph |
| `openclaw.py` | 第 15 课运行时握手 |
| `schemas.py` | 第 16 课结构化 Prompt |
| `tools.py` / `mcp.py` | 第 17 课 Tool 与 MCP |
| `skills.py` | 第 18 课 Skill 链式联动 |
| `rag.py` + `knowledge/` | 第 19–20 课 RAG |

依赖：Python 3.9+、`pydantic` 2.x（本课包已按此验收）。
