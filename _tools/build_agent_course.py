# -*- coding: utf-8 -*-
"""生成第13–20课讲义、课后练习、教案、README、实验说明。运行一次即可。"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BOOT = """import sys
from pathlib import Path

COURSE = Path.cwd().resolve()
if COURSE.name.startswith("第"):
    COURSE = COURSE.parent
if str(COURSE) not in sys.path:
    sys.path.insert(0, str(COURSE))
print("已加入路径:", COURSE)
print("请从本课文件夹启动内核。未配置 OPENAI_BASE_URL 时使用教学 Fake 端点，不要求 GPU。")
"""

EMPTY_K = """# Write your predictions, reasoning, or solution here.
# Keep deliberately faulty snippets in Markdown; run your corrected code here.
"""

EMPTY_R = """# R.1–R.3: Write and verify your predictions here.
"""

META = [
    {
        "folder": "第13课-模型私有化部署与Serving",
        "num": "13",
        "theme": "模型私有化部署与Serving",
        "title": "模型私有化部署与 Serving",
        "stage": "阶段零 · 前置基座",
        "accept": "探活通过，模型列表含 qwen2.5，JSON 约束输出 ping=ok。",
        "note": "课堂用教学 Fake 端点即可验收；可选对接本机 Ollama / vLLM 的 /v1。环境样例见 serving.env.example。",
        "hw_extra": "可选阅读同目录 serving.env.example。不要把真实密钥写进笔记本。",
        "score": "前置基座，为后续任务提供稳定 /v1 端点",
    },
    {
        "folder": "第14课-LangGraph状态图与Agent骨架",
        "num": "14",
        "theme": "LangGraph状态图",
        "title": "LangGraph 状态图与 Agent 骨架",
        "stage": "阶段一 · 前置理论",
        "accept": "条件边走出 agent→tool→finalize；Checkpointer 累积 messages；recursion_limit 触发熔断。",
        "note": "教学 StateGraph 在 agent_lab.graph，接口对齐 LangGraph 的 Node / Edge / 条件边。",
        "hw_extra": "不要改 agent_lab 源码来“过验收”；在笔记本里自己构图。",
        "score": "前置理论，后续 OpenClaw 直接复用状态图",
    },
    {
        "folder": "第15课-OpenClaw运行时初始化",
        "num": "15",
        "theme": "OpenClaw运行时",
        "title": "OpenClaw 运行时初始化",
        "stage": "阶段二 · 任务一 1.1 / 10分",
        "accept": "OpenClaw Client 握手探活成功，并打印首轮状态迁移日志。",
        "note": "把 LangGraph 的 thread / reducer 映射到 OpenClawConfig。",
        "hw_extra": "评分对照：Client 初始化 + 握手 + 首轮 state_log（10分）。",
        "score": "10分",
    },
    {
        "folder": "第16课-Pydantic结构化Prompt",
        "num": "16",
        "theme": "Pydantic结构化Prompt",
        "title": "Pydantic 结构化 Prompt",
        "stage": "阶段二 · 任务一 1.2 / 15分",
        "accept": "三级梯度：扁平用户、嵌套工单、脏金额归一化与对抗拦截全部通过。",
        "note": "Schema 写入 Prompt，再用 model_validate 验收模型输出。",
        "hw_extra": "评分对照：基础 5 分、进阶 5 分、高难 5 分。",
        "score": "15分",
    },
    {
        "folder": "第17课-自定义Tool与MCP接入",
        "num": "17",
        "theme": "自定义Tool与MCP",
        "title": "自定义 Tool 与 MCP 接入",
        "stage": "阶段三 · 任务二 2.1+2.2 / 15分",
        "accept": "导出 Function Calling Schema；参数/业务异常隔离；MCP 握手读出 Tools 与 Resources。",
        "note": "Tool 失败必须返回标准化错误字段，禁止让整个程序崩溃。",
        "hw_extra": "评分对照：Tool 10 分 + MCP 能力发现 5 分。",
        "score": "15分",
    },
    {
        "folder": "第18课-Skill封装与链式联动",
        "num": "18",
        "theme": "Skill封装与链式联动",
        "title": "Skill 封装与链式联动",
        "stage": "阶段三 · 任务二 2.3 / 20分",
        "accept": "单工具命中、双工具串行流转、模糊指令自愈三例全部成功。",
        "note": "Skill 是对 Tool / MCP 的业务组合，不是再写一套 HTTP 客户端。",
        "hw_extra": "评分对照：基础 6 分、进阶 7 分、高难自愈 7 分。",
        "score": "20分",
    },
    {
        "folder": "第19课-RAG检索流水线",
        "num": "19",
        "theme": "RAG检索流水线",
        "title": "RAG 检索流水线",
        "stage": "阶段四 · 任务三 3.1 / 15分",
        "accept": "知识库完成分块入库；Retriever 封装为 Tool 并可被调用；续航类问题命中手册切片。",
        "note": "知识库默认在课程根目录 agent_lab/knowledge/；本课另有副本 kb/ 供课后独立读取。",
        "hw_extra": "课后请优先读取本课 kb/ 目录，不要依赖讲义里已经建好的 retriever 变量。",
        "score": "15分",
    },
    {
        "folder": "第20课-RAG调优与结构化溯源",
        "num": "20",
        "theme": "RAG调优与结构化溯源",
        "title": "RAG 调优与结构化溯源",
        "stage": "阶段四 · 任务三 3.2 / 25分",
        "accept": "单文档带 chunk_id 溯源；跨文档聚合；越界提问返回 FallbackResponse。",
        "note": "混合检索（向量余弦 + BM25）后截断重排；回答必须带佐证或规范兜底。",
        "hw_extra": "评分对照：基础 7 分、进阶 9 分、高难兜底 9 分。",
        "score": "25分",
    },
]


def lines(text: str):
    if not text.endswith("\n"):
        text += "\n"
    return text.splitlines(keepends=True)


def md(text: str, cid: str):
    return {"cell_type": "markdown", "id": cid, "metadata": {}, "source": lines(text)}


def code(text: str, cid: str):
    return {
        "cell_type": "code",
        "id": cid,
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": lines(text),
    }


def dump_nb(path: Path, cells):
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": cells,
    }
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


def k_md(n: int, questions, extra=""):
    body = "\n".join("%d. **K%s.%d** %s" % (i, n, i, q) for i, q in enumerate(questions, 1))
    return "### 易错点与练习\n\n%s\n\n**作答：** ____。\n%s" % (body, extra)


def section_cells(prefix, n, title, theory, case_intro, case_code, explain, questions):
    cells = [
        md("## %s. %s\n\n### 理论知识\n\n%s\n\n### 案例：%s\n" % (n, title, theory, case_intro), "%s-s%s-t" % (prefix, n)),
        code(case_code, "%s-s%s-c" % (prefix, n)),
        md("### 讲解\n\n%s\n\n%s" % (explain, k_md(n, questions)), "%s-s%s-e" % (prefix, n)),
        code(EMPTY_K, "%s-s%s-k" % (prefix, n)),
    ]
    return cells


def lecture_shell(m, recap, goals, table, recap_qs, footer_ban, sections, p1_title, p1s, close):
    prefix = "c" + m["num"]
    hw_name = "chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])
    head = """# 第%s课：%s

本笔记本是课堂讲义。每个知识点包含：理论知识、案例代码、讲解、易错点与练习。综合练习 P1 使用课程根目录的教学运行时 [`agent_lab`](../agent_lab/README.md)。课后独立练习见 [%s](%s)。

**阶段定位**：%s。%s

%s

## 学习目标

%s

## 学习知识点

%s

## 基础回顾与案例提问

%s

%s

使用 Python 3；需要 `pydantic`。从本课文件夹启动内核。本课不要求 GPU，也不强制安装 `langgraph` / `openai`。未配置私有化端点时，`get_client()` 返回进程内 Fake。不要使用 pandas。综合练习不要抄 `experiment.py` 的整段答案，按题面逐步完成。
""" % (
        m["num"],
        m["title"],
        hw_name,
        hw_name,
        m["stage"],
        m["score"],
        recap,
        "\n".join("%d. %s" % (i, g) for i, g in enumerate(goals, 1)),
        table,
        recap_qs,
        footer_ban,
    )
    cells = [md(head, prefix + "-h"), code(EMPTY_R, prefix + "-r"), code(BOOT, prefix + "-boot")]
    for sec in sections:
        cells.extend(section_cells(prefix, *sec))
    cells.append(md("## 综合练习：%s\n\n按 P1.1 → P1.2 → P1.3 顺序完成。每步都要能独立看出你做了什么。\n" % p1_title, prefix + "-p0"))
    for i, (title, body, stub) in enumerate(p1s, 1):
        cells.append(md("### P1.%d　%s\n\n%s\n" % (i, title, body), "%s-p1%d-m" % (prefix, i)))
        cells.append(code(stub, "%s-p1%d-c" % (prefix, i)))
    cells.append(md(close, prefix + "-z"))
    return cells


def hw_shell(m, env_extra, p1, p2, p3):
    prefix = "h" + m["num"]
    lec = "chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])
    head = """# 第%s课：课后练习

**姓名：** ____　**学号：** ____　**班级：** ____　**日期：** ____

环境：Python 3，Jupyter Notebook 或课程平台；需要 `pydantic`。请从本课文件夹启动内核，并保证能 `import agent_lab`（课程根目录在上一级）。不要依赖课堂讲义里已经构造好的变量。未配置 `OPENAI_BASE_URL` 时使用教学 Fake 端点，**不要求 GPU**。

先修：第 13 课起的 Serving / 状态图概念视本课需要。本练习与 [%s](%s) 相互独立：请在自己的解答中重新导入。不要使用 pandas、不要改 `agent_lab` 源码来硬过题。

P1、P2 为必做课后任务；P3 为选做。完成后请重启内核，按顺序运行自己的解答单元格。故意写错的代码片段请保留在 Markdown 中，不要放进最终可运行流程。

%s

提交时另存为 `第%s课课后练习_<学号>.ipynb`。不要求使用 AI；若使用过，请简要记录它帮了什么、你又核对了什么。
""" % (m["num"], lec, lec, env_extra, m["num"])
    cells = [md(head, prefix + "-h"), code(BOOT, prefix + "-boot")]
    for tag, title, flag, body, stub, note in [
        ("P1", p1[0], "必做 · 约 15–20 分钟", p1[1], p1[2], p1[3]),
        ("P2", p2[0], "必做 · 约 15–20 分钟 · 依赖 P1", p2[1], p2[2], p2[3]),
        ("P3", p3[0], "选做 · 约 10 分钟 · 依赖 P1", p3[1], p3[2], p3[3]),
    ]:
        cells.append(md("## %s · %s\n**%s**\n\n%s\n" % (tag, title, flag, body), "%s-%s-m" % (prefix, tag.lower())))
        cells.append(code(stub, "%s-%s-c" % (prefix, tag.lower())))
        cells.append(md("### %s · 说明与验证\n\n%s\n" % (tag, note), "%s-%s-n" % (prefix, tag.lower())))
    cells.append(
        md(
            """## 提交前核对

- P1、P2 已在新内核下从头跑通；文字作答与运行输出都保留。
- 没有把真实 API Key 写进笔记本。
- 选做 P3 已明确标注：已做 / 未做：____。
""",
            prefix + "-z",
        )
    )
    return cells


def write_docs(m):
    folder = ROOT / m["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    lec = "chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])
    hw = "chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])
    readme = """# {folder}

**主题**：{title}

**当堂验收**：{accept}

**说明**：课堂讲义与本课材料同目录；课后练习使用题面指定的运行时与数据。从该文件夹启动内核。

{note}
## 本课文件

| 文件 | 用途 |
|------|------|
| `{lec}` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `{hw}` | 课后练习：P1、P2 必做，P3 选做 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
""".format(folder=m["folder"], title=m["title"], accept=m["accept"], note=m["note"] + "\n", lec=lec, hw=hw)
    if m["num"] == "13":
        readme = readme.replace("| `experiment.py` | 验收脚本 |", "| `serving.env.example` | 可选：真实 /v1 端点环境变量样例 |\n| `experiment.py` | 验收脚本 |")
    if m["num"] in ("19", "20"):
        readme = readme.replace("| `experiment.py` | 验收脚本 |", "| `kb/` | 产品手册 / 价格 / 政策，课后独立读取 |\n| `experiment.py` | 验收脚本 |")
    (folder / "README.md").write_text(readme, encoding="utf-8")
    intro = """# 实验说明 · {title}

你将创造什么：完成本课实验后，应能做到——{accept}

课堂讲义：打开 `{lec}`。每个知识点有理论、案例和练习；综合练习 P1 使用 `agent_lab`。

课后练习：打开 `{hw}`。P1、P2 必做，P3 选做。不要依赖讲义里已经构造好的变量。

{hw_extra}

验收脚本：在本文件夹执行 `python3 experiment.py`，看到 `本课验收通过`。

阶段与评分：{stage}（{score}）。时间盒见本课 `教案.md`。
""".format(**m, lec=lec, hw=hw)
    (folder / "实验说明.md").write_text(intro, encoding="utf-8")


def write_plans():
    plans = {
        "13": dict(
            id="agent-l13",
            title="课次 L13 模型私有化部署与 Serving",
            purpose="把开源模型收成 OpenAI 兼容 /v1，并用 Pydantic 探活",
            goals=["说明私有化 Serving 与云厂商 API 的差别", "列出 /v1/models 与 /v1/chat/completions", "用 Pydantic 校验 JSON 约束输出"],
            skills=["能跑通探活脚本并解释 ok / json_ok", "能把 Base URL、Key、超时写成配置而不是写死在业务里"],
            prep=["已完成第 1–12 课 Python 基础", "本机有 pydantic；有无 GPU 均可"],
            skip=["CUDA 编译、量化细节、多卡并行"],
            box=[
                ("0–15", "为什么要私有化：数据不出域、接口要稳定"),
                ("15–50", "OpenAI 兼容形状；Fake 与 Http 两种客户端"),
                ("50–80", "HealthReport + JSON schema 探活"),
                ("80–90", "收束：真实 Ollama/vLLM 只改环境变量"),
            ],
            traps=[
                ("找不到 agent_lab", "从本课文件夹启动内核，sys.path 指到课程根"),
                ("真实端点 404", "Base URL 必须含 /v1，不要写成服务根路径"),
                ("模型胡乱输出", "response_format=json_object 后再 Pydantic 校验"),
            ],
        ),
        "14": dict(
            id="agent-l14",
            title="课次 L14 LangGraph 状态图与 Agent 骨架",
            purpose="把 Agent 讲成状态图，而不是一串 print",
            goals=["用 reducer 声明状态如何合并", "画出 Node / Edge / 条件边", "用 recursion_limit 与 MemorySaver 处理循环与多轮"],
            skills=["能手写 agent-tool-finalize 闭环", "能解释 messages 为何是累积而 user 是覆盖"],
            prep=["第 13 课探活通过"],
            skip=["LangGraph 云部署、子图、Human-in-the-loop 完整产品化"],
            box=[
                ("0–15", "Agent = 状态图：对照流程图"),
                ("15–55", "channels / add_node / add_conditional_edges"),
                ("55–80", "Checkpointer 多轮 + 熔断演示"),
                ("80–90", "收束：下一课把图嵌进 OpenClaw"),
            ],
            traps=[
                ("条件边走错", "router 返回的标签必须出现在 mapping 里"),
                ("死循环", "课堂先把 recursion_limit 调到 3 看报错，再改边"),
                ("次轮丢掉首轮消息", "messages 必须用 add_messages，不能 overwrite"),
            ],
        ),
        "15": dict(
            id="agent-l15",
            title="课次 L15 OpenClaw 运行时初始化",
            purpose="完成 Client 握手并打印首轮状态迁移日志",
            goals=["把 StateGraph 配置映射到 OpenClawConfig", "接入阶段零端点：Base URL、Key、超时", "读懂 state_log"],
            skills=["能初始化 Client 并 handshake", "能指出日志里的 turn / node / runtime"],
            prep=["第 13–14 课"],
            skip=["OpenClaw 商业控制台、多租户鉴权"],
            box=[
                ("0–15", "OpenClaw 与 LangGraph 的对应表"),
                ("15–50", "Config 字段：端点、密钥、超时、session_id"),
                ("50–80", "handshake + run_turn，投影 state_log"),
                ("80–90", "对照 10 分评分标准收束"),
            ],
            traps=[
                ("握手失败仍继续聊天", "先 assert report.ok"),
                ("日志为空", "确认走了 run_turn 而不是只构造了 Client"),
                ("timeout 过小", "课堂 Fake 为 0 延迟；真实端点建议 ≥ 8s"),
            ],
        ),
        "16": dict(
            id="agent-l16",
            title="课次 L16 Pydantic 结构化 Prompt",
            purpose="三级梯度测通 Schema 约束输出",
            goals=["用 BaseModel/Field 生成 JSON Schema 并写入 Prompt", "扁平、嵌套、自定义校验器三档都跑通", "对抗脏数据时拦截而不是静默 NaN"],
            skills=["能解释 phone 去空格", "能查出 total 与明细不一致", "能把 ￥1,299.00 归一成 1299.0"],
            prep=["第 15 课握手通过"],
            skip=["Pydantic v1、dataclass 替代方案"],
            box=[
                ("0–15", "Schema 即契约，不是事后正则"),
                ("15–55", "UserProfile / TicketAnalysis 两档演示"),
                ("55–80", "DirtyAmount 与“免费送”拦截"),
                ("80–90", "15 分评分对照"),
            ],
            traps=[
                ("把校验写在 Prompt 里却不跑 model_validate", "模型输出必须再走一遍 Schema"),
                ("嵌套 list 忘记子模型", "LineItem 要单独定义"),
                ("校验器 mode 不对", "归一化脏字符串用 mode='before'"),
            ],
        ),
        "17": dict(
            id="agent-l17",
            title="课次 L17 自定义 Tool 与 MCP 接入",
            purpose="契约化 Tool + MCP 能力发现",
            goals=["写出 ArgsSchema / ResultSchema", "异常隔离成错误文本", "MCP 握手列出 Tools 与 Resources"],
            skills=["能 export_function_schema", "能解释 stdio 握手不等于已经调用了工具"],
            prep=["第 16 课 Schema"],
            skip=["真实 npx MCP 进程管理、SSE 重连的工程细节"],
            box=[
                ("0–20", "Tool 契约与 Function Calling JSON"),
                ("20–55", "短 SKU / 未知 SKU 两次隔离"),
                ("55–80", "MCPClient.handshake 读元数据"),
                ("80–90", "15 分评分对照"),
            ],
            traps=[
                ("校验失败直接 raise", "必须返回 ResultSchema(ok=False)"),
                ("把业务异常当成 Python 崩溃", "未知 SKU 也走 error 字段"),
                ("只打印 server 名", "必须列出 tools 与 resources 清单"),
            ],
        ),
        "18": dict(
            id="agent-l18",
            title="课次 L18 Skill 封装与链式联动",
            purpose="把多个 Tool 收成可评分的业务 Skill",
            goals=["单工具精准命中", "A 的 Pydantic 输出无缝注入 B", "模糊指令失败后自修正"],
            skills=["能读懂 quote_skill 的数据流", "能指出自愈前后的 first_error"],
            prep=["第 17 课 Tool"],
            skip=["多 Agent 辩论、异步并发编排"],
            box=[
                ("0–15", "Skill ≠ Tool：组合与清洗"),
                ("15–50", "基础命中 + 进阶双工具"),
                ("50–80", "self_correct_quote 对抗“小部件X”"),
                ("80–90", "20 分评分对照"),
            ],
            traps=[
                ("第二步用手改数字", "必须用第一步校验后的字段"),
                ("自愈直接从别名开始", "高难要求先失败再修，attempts==2"),
                ("库存不足仍报价成功", "本课库存表以 STOCK 为准，未知 SKU 必须失败"),
            ],
        ),
        "19": dict(
            id="agent-l19",
            title="课次 L19 RAG 检索流水线",
            purpose="分块、入库、Retriever 封装为 Tool",
            goals=["按段落分块并赋予 chunk_id", "把检索挂成 Agent 可调用的 Tool", "抽检续航问题命中手册"],
            skills=["能解释 doc_id::idx", "能把 hits 放进 Tool 的 ResultSchema"],
            prep=["第 17–18 课"],
            skip=["Faiss GPU、百万级向量运维"],
            box=[
                ("0–15", "为何不能把整本手册塞进 Prompt"),
                ("15–55", "chunk → Retriever → Tool"),
                ("55–80", "命中率抽检：续航 / 48 小时"),
                ("80–90", "15 分评分对照"),
            ],
            traps=[
                ("中文按空格分词", "教学 tokenize 使用汉字 bigram"),
                ("Agent 直接编答案", "本课强制走 rag_search Tool"),
                ("课后读错目录", "课后用本课 kb/，不要混用讲义变量"),
            ],
        ),
        "20": dict(
            id="agent-l20",
            title="课次 L20 RAG 调优与结构化溯源",
            purpose="混合检索、重排、带出处回答与幻觉兜底",
            goals=["说明 BM25 + 向量为何要混合", "SourcedAnswer 必须带 chunk_id 与 quote", "越界问题返回 FallbackResponse"],
            skills=["能对比两款 Widget 并引用至少两个文档", "能拒绝天气类越界提问"],
            prep=["第 19 课流水线可用"],
            skip=["微调 LLM、商业 Rerank API"],
            box=[
                ("0–15", "命中不准时先调检索再怪模型"),
                ("15–55", "基础单文档 + 进阶跨文档"),
                ("55–80", "高难：天气问题走 fallback"),
                ("80–90", "25 分评分对照与学期收束"),
            ],
            traps=[
                ("有文本就算溯源", "必须有 chunk_id 与原文片段"),
                ("越界仍拼答案", "OUT_OF_CORPUS 关键词直接兜底"),
                ("跨文档只引用同一 md", "对比题至少两个 doc_id"),
            ],
        ),
    }
    for m in META:
        p = plans[m["num"]]
        goals = "\n".join("%d. %s" % (i, g) for i, g in enumerate(p["goals"], 1))
        skills = "\n".join("%d. %s" % (i, g) for i, g in enumerate(p["skills"], 1))
        prep = "\n".join("%d. %s" % (i, g) for i, g in enumerate(p["prep"], 1))
        skip = "\n".join("- %s" % x for x in p["skip"])
        box = "\n".join("| %s | %s |" % (a, b) for a, b in p["box"])
        traps = "\n".join("| %s | %s |" % (a, b) for a, b in p["traps"])
        text = """---
id: {id}
title: {title}
purpose: {purpose}
created: 2026-09-16
status: active
owner: python-agent-lab
tags: [python, agent, lesson-plan, l{num}]
---

# {title}

**对应阶段** {stage}

**建议学时** 3

## 目标

**知识目标**

{goals}

**能力目标**

{skills}

**素养目标**

1. 把模型当不可靠组件：接口、Schema、熔断、溯源缺一不可

**前置准备**

{prep}

## 当堂不讲

{skip}

## 时间盒（90 分钟）

| 分钟 | 内容 |
|------|------|
{box}

## 实验

必做：讲义案例 + 综合练习 P1。破坏性：超时、校验失败、死循环、越界提问（按课次出现）。

## 卡点

| 现象 | 处置 |
|------|------|
{traps}

## 当堂验收

{accept}

## 接口

教学运行时：`agent_lab/`。验收：`python3 experiment.py`。
""".format(
            id=p["id"],
            title=p["title"],
            purpose=p["purpose"],
            num=m["num"],
            stage=m["stage"],
            goals=goals,
            skills=skills,
            prep=prep,
            skip=skip,
            box=box,
            traps=traps,
            accept=m["accept"],
        )
        (ROOT / m["folder"] / "教案.md").write_text(text, encoding="utf-8")


def copy_kb():
    src = ROOT / "agent_lab" / "knowledge"
    for num in ("19", "20"):
        m = next(x for x in META if x["num"] == num)
        dest = ROOT / m["folder"] / "kb"
        dest.mkdir(parents=True, exist_ok=True)
        for path in src.glob("*.md"):
            shutil.copy2(path, dest / path.name)


def build_lectures():
    m = META[0]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="前 12 课把表洗干净、把函数写对。从本课起，程序要**调用模型**。模型不是函数：同一输入可能换措辞，必须用协议和 Schema 把它关进笼子。",
            goals=[
                "说明私有化部署要把模型收成稳定的推理服务，而不是在笔记本里临时 print。",
                "指出 OpenAI 兼容端点至少包含 `/v1/models` 与 `/v1/chat/completions`。",
                "使用 Pydantic `HealthReport` 做自动化探活，记录延迟与 JSON 约束是否成功。",
                "在未配置真实 GPU 服务时，能解释 Fake 端点为何仍能完成本课验收。",
            ],
            table="""| 端点 | 探活 | 约束输出 |
| --- | --- | --- |
| Base URL 指向 /v1 | 列出 model id | response_format=json_object |
| Key 与超时写在配置里 | 记录 latency_ms | Pydantic 再校验 |
| Fake 与 Http 同一形状 | ok 与 json_ok 分开 | ping / serving 字段 |""",
            recap_qs="""1. **R.1** 若业务代码里写死 `http://127.0.0.1:11434/v1`，换到 vLLM 的 8000 端口时要改几处？配置项应该叫什么？
2. **R.2** `/v1/models` 成功是否等于聊天也能返回合法 JSON？还缺哪一步？
3. **R.3** 模型返回 `{"ping":"ok"}` 但漏了 `serving` 时，`HealthReport.json_ok` 应是 True 还是 False？""",
            footer_ban="本课不讲 CUDA、量化训练或多卡调度。真实 Ollama/vLLM 只作为可选对接。",
            sections=[
                (
                    1,
                    "为什么要私有化 Serving",
                    "**Serving 的意思是：模型作为服务常驻，业务只认 URL。** 数据可以不出域，接口形状要对齐，这样后面的 Agent 不用关心背后是 Qwen 还是 DeepSeek。",
                    "对比“直接在脚本里假想有模型”和“先探活再调用”",
                    """print("业务不要写: model.predict(prompt)")
print("业务要写: POST {BASE_URL}/chat/completions")
print("验收看两件事: 列表里有模型, 回复能通过 Schema")""",
                    "把模型当成会失败的网络依赖：超时、空列表、非 JSON 都可能发生。探活脚本的职责是在 Agent 启动前把这些失败变成结构化报告。",
                    ["Serving 和“在 Jupyter 里 import 一个本地权重文件”有何不同？", "为什么实训产出要写“稳定推理服务”，而不是“能聊天”？"],
                ),
                (
                    2,
                    "OpenAI 兼容的 /v1",
                    "**兼容不是营销词，是两套路径。** 列表用 GET `/models`，对话用 POST `/chat/completions`。请求体里有 `model`、`messages`；JSON 约束常加 `response_format`。",
                    "看 FakeOpenAI 的返回形状",
                    """from agent_lab.mock_openai import FakeOpenAI
client = FakeOpenAI()
print(client.base_url)
print(client.models.list()["data"])
resp = client.chat.completions.create(
    model="qwen2.5",
    messages=[{"role": "user", "content": "健康探活"}],
    response_format={"type": "json_object"},
)
print(resp["choices"][0]["message"]["content"])""",
                    "`choices[0].message.content` 仍是字符串。兼容端点只保证外层信封，不保证业务字段合法，所以还要 Pydantic。",
                    ["若 Base URL 写成 `http://127.0.0.1:11434` 而服务实际挂在 `/v1`，列表请求会打到哪？", "`messages` 为什么是列表而不是一个长字符串？"],
                ),
                (
                    3,
                    "Fake 客户端与 Http 客户端",
                    "**同一套调用形状，两种实现。** `get_client()` 读环境变量 `OPENAI_BASE_URL`；没有则 Fake；有但连不上则 fake-fallback。",
                    "打印当前端点来源",
                    """from agent_lab.mock_openai import get_client
client, source = get_client()
print(source, getattr(client, "base_url", None))""",
                    "课堂默认 `source == 'fake'` 就算达标。连上真实 Ollama 时 source 变为 `http`。不要为了“看起来更真”而在没服务时强行 Http。",
                    ["为什么教学要保留 Fake，而不是强制每人安装 7B 模型？", "Key 写成 `sk-local` 在内网私有化里通常扮演什么角色？"],
                ),
                (
                    4,
                    "Pydantic 探活报告",
                    "**探活结果也是一份 Schema。** `HealthReport` 记录 ok、模型 id、延迟、json_ok、detail、source。自动化脚本只认字段，不认 print 的心情。",
                    "调用 probe()",
                    """from agent_lab.health import probe
report = probe()
print(report.model_dump())""",
                    "`ok` 需要“有模型”且“JSON 约束成功”。只有列表成功但聊天胡言，json_ok 为 False，整次探活不算过。",
                    ["latency_ms 在 Fake 下接近 0 说明了什么？能否用它判断真实 GPU 是否够快？", "detail 里为什么要同时保留原始字符串和校验后的 JSON？"],
                ),
                (
                    5,
                    "JSON 约束输出",
                    "**约束分两层。** 第一层告诉模型“只输出 JSON”；第二层用 `ProbePayload` 检查字段类型与取值。",
                    "手动校验一段回复",
                    """import json
from agent_lab.health import ProbePayload
raw = '{"ping":"ok","serving":true}'
print(ProbePayload.model_validate(json.loads(raw)))""",
                    "模型偶尔会包 markdown 代码块或加解说。探活脚本必须把这种失败写进 detail，而不是让 `json.loads` 把整个 Agent 拉倒。",
                    ["若 raw 是 `好的，服务正常`，应记 json_ok=False 还是手写 True？", "`serving` 必须是布尔值，写成字符串 `\"true\"` 能否通过？先预测再验证。"],
                ),
                (
                    6,
                    "超时策略",
                    "**超时是配置，不是运气。** `timeout_s` 传到 Http 客户端。内网小模型常见 8 秒；冷启动可能更长。课堂 Fake 不消耗等待。",
                    "看 probe 的参数",
                    """from agent_lab.health import probe
print(probe(timeout_s=5.0).ok)""",
                    "把超时写进 OpenClawConfig 后，第 15 课不用再改探活代码。这就是阶段零要先封装 Serving 的原因。",
                    ["超时过短会出现什么用户可见现象？", "为什么不建议在每次聊天时写不同的 timeout 魔法数？"],
                ),
                (
                    7,
                    "可选：对接 Ollama / vLLM",
                    "**真实服务只改环境，不改业务。** Ollama 默认 `http://127.0.0.1:11434/v1`；vLLM 的 OpenAI 入口常见 8000 端口。样例见 `serving.env.example`。",
                    "读取环境变量（没有也不报错）",
                    """import os
print("OPENAI_BASE_URL=", os.environ.get("OPENAI_BASE_URL") or "(未设置，使用 Fake)")""",
                    "助教验收以 `python3 experiment.py` 为准。你本机有 GPU 可以加分演示，但不能让没 GPU 的同学无法交作业。",
                    ["vLLM 与 Ollama 对 `/v1` 的职责有何相同之处？", "为什么作业禁止把真实 Key 贴进 ipynb？"],
                ),
                (
                    8,
                    "本课验收口径",
                    "**过关句子是 `本课验收通过`。** 断言：`report.ok`、`report.json_ok`、模型列表含 `qwen2.5`。",
                    "对照验收字段",
                    """from agent_lab.health import probe
r = probe()
print("source", r.source)
print("models", r.model_ids)
print("json_ok", r.json_ok, r.detail)""",
                    "后续每一课的 Client 都经这里取端点。Serving 不稳，后面的 Tool / RAG 全是噪音。",
                    ["若有人把 qwen2.5 改成别的默认 id，experiment.py 会在哪一条断言失败？", "json_ok 与 ok 同时打印的好处是什么？"],
                ),
            ],
            p1_title="探活一条龙",
            p1s=[
                (
                    "准备客户端",
                    "从本课文件夹启动内核，加入课程根目录到 `sys.path`。调用 `get_client()`，打印 `source` 与 `base_url`。",
                    "# P1.1: get_client and print source / base_url.\n",
                ),
                (
                    "列出模型并聊天",
                    "列出 model id。向聊天接口发送“健康探活”，`response_format` 设为 `json_object`，打印原始 content。",
                    "# P1.2: list models and create a JSON completion.\n",
                ),
                (
                    "写成 HealthReport",
                    "调用 `probe()`（或自己构造同等字段），确认 `ok` 与 `json_ok`。不要把 True 写死在代码里。",
                    "# P1.3: probe() and confirm ok / json_ok.\n",
                ),
            ],
            close="课后请打开 [chapter13_模型私有化部署与Serving_课后练习.ipynb](chapter13_模型私有化部署与Serving_课后练习.ipynb)。P1 自己写探活字段说明，P2 制造一次 JSON 失败并记录，P3 选做阅读环境变量样例。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 教学模块：`agent_lab.health`、`agent_lab.mock_openai`。",
            (
                "自己走一遍探活并解释字段",
                "调用 `probe()`，打印 `ok`、`model_ids`、`json_ok`、`source`、`latency_ms`。用两三句话说明：为什么“列出模型成功”还不够，必须看 `json_ok`。不要把验收结果写死成常量。",
                "# P1: probe and explain fields.\n",
                "应交：可运行输出；字段含义；source 在未配置环境变量时应为 fake 或你实际连上的 http。",
            ),
            (
                "记录一次 JSON 约束失败",
                "构造一段**不是**合法 ProbePayload 的字符串（例如缺少 serving、或根本不是 JSON）。说明若探活脚本不校验，后面的 Agent 会怎样。可以对照 `ProbePayload.model_validate` 的报错，不要让未捕获异常中断你最终提交的内核。",
                "# P2: demonstrate a JSON / schema failure without crashing the final run.\n",
                "应交：失败样例（Markdown 或隔离后的代码）；报错要点；你如何隔离。若过程未出错，分析提供案例并标注“提供案例”。",
            ),
            (
                "选做：真实端点",
                "若本机已有 Ollama 或 vLLM 的 /v1，设置环境变量后再 `probe()`，对比 source 与模型列表。没有 GPU 则写“未做”并说明原因，不扣选做分。",
                "# P3 optional: probe a real /v1 endpoint if you have one.\n",
                "若选做，应交：Base URL（可打码 Key）、source、模型 id 摘要。不要提交真实密钥。",
            ),
        ),
    )

    m = META[1]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="第 13 课解决“模型在哪里、接口长什么样”。本课解决“Agent 怎么想下一步”。答案不是再写一个更长的 if-else，而是**状态图**。",
            goals=[
                "用 Pydantic 或 TypedDict 思路声明全局状态，并指出哪些字段用累积 reducer、哪些用覆盖。",
                "用 StateGraph 连接 Agent 节点与 Tool 节点，形成闭环。",
                "写出条件边：根据 `need_tool` 决定去 tool 还是 finalize。",
                "设置 recursion_limit，并用 MemorySaver 做同 thread 的多轮恢复。",
            ],
            table="""| 状态 | 拓扑 | 熔断与记忆 |
| --- | --- | --- |
| channels 声明字段 | add_node | recursion_limit |
| add_messages 累积 | add_edge | MemorySaver |
| overwrite 覆盖 | add_conditional_edges | thread_id |""",
            recap_qs="""1. **R.1** 若把用户本轮输入和历史消息放进同一个列表并每次覆盖整个列表，多轮对话会丢什么？
2. **R.2** 条件边的 router 返回 `"tool"`，但 mapping 只有 `{"end": "finalize"}`，运行时会发生什么？
3. **R.3** 节点自己指向自己且 recursion_limit=3，应看到什么异常？""",
            footer_ban="教学图在 `agent_lab.graph`。真实 LangGraph 的 API 同名概念可对照，本课不要求 pip install langgraph。",
            sections=[
                (
                    1,
                    "Agent 本质是状态图",
                    "**节点做一件事，边决定下一件事。** START 进入 agent；agent 可去 tool 或 finalize；finalize 到 END。这就是最小 Agent。",
                    "三个名字先记熟",
                    """print("START -> agent")
print("agent --(need_tool)--> tool -> finalize -> END")
print("agent --(else)--> finalize -> END")""",
                    "不要把“会说话的模型”等同于 Agent。没有状态和边，只是单次补全。",
                    ["Tool 节点如果直接回到自己而不经过 agent，会缺什么决策？", "END 是节点函数还是图的终止标记？"],
                ),
                (
                    2,
                    "状态与 Reducer",
                    "**Reducer 回答：新旧值如何合成。** `messages` 用 `add_messages` 做列表拼接；`need_tool`、`result` 用覆盖。",
                    "看两种合并",
                    """from agent_lab.graph import add_messages
print(add_messages(["a"], ["b"]))
print(add_messages(None, ["first"]))""",
                    "第 14 课验收会打印次轮 `messages`：里面应能看到首轮 think/tool/final，这就是 reducer 的证据。",
                    ["user 本轮文本应该累积还是覆盖？为什么？", "trace 若用覆盖，调试时会丢掉什么？"],
                ),
                (
                    3,
                    "Node：只返回增量",
                    "**节点函数接收当前状态，返回要合并的增量字典。** 不要在节点里偷偷改传入的 dict 又同时 return，教学里统一 return 更新。",
                    "一个只思考的 agent 节点",
                    """def agent(state):
    text = state.get("user", "")
    need = "库存" in text
    return {"messages": ["think:" + text], "need_tool": need}
print(agent({"user": "查询库存"}))""",
                    "节点保持短小：判断意图、调用工具、收束回复，分成三个节点，条件边才画得清。",
                    ["若 agent 直接在函数里 print 库存数字而不更新 state，finalize 读得到吗？", "`need_tool` 为什么不要放进 messages 字符串里用 in 去猜？"],
                ),
                (
                    4,
                    "普通边与条件边",
                    "**普通边是固定下一站。条件边先跑 router，再用 mapping 翻译成节点名。**",
                    "router 必须返回 mapping 的键",
                    """def route(state):
    return "tool" if state.get("need_tool") else "end"
print(route({"need_tool": True}), route({"need_tool": False}))""",
                    "标签 end 不等于 END 常量，它只是 mapping 里的钥匙，通常映射到 finalize。",
                    ["mapping 写成 `{\"tool\": \"tool\"}` 却漏了 `end`，用户打招呼时会怎样？", "START 到 agent 应该用普通边还是条件边？"],
                ),
                (
                    5,
                    "搭一条最小闭环",
                    "**agent →（条件）tool/finalize，tool → finalize，finalize → END。**",
                    "编译并跑一轮",
                    """from agent_lab.graph import END, START, StateGraph, add_messages

channels = {"messages": add_messages, "trace": add_messages, "need_tool": lambda o, n: n, "result": lambda o, n: n}

def agent(state):
    text = state.get("user", "")
    return {"messages": ["think:" + text], "need_tool": "库存" in text}

def tool_node(state):
    return {"messages": ["tool:stock=12"], "result": "WIDGET-X=12"}

def finalize(state):
    return {"messages": ["final:" + str(state.get("result") or "no-tool")]}

g = StateGraph(channels)
g.add_node("agent", agent).add_node("tool", tool_node).add_node("finalize", finalize)
g.add_edge(START, "agent")
g.add_conditional_edges("agent", lambda s: "tool" if s.get("need_tool") else "end", {"tool": "tool", "end": "finalize"})
g.add_edge("tool", "finalize")
g.add_edge("finalize", END)
app = g.compile(recursion_limit=8)
out = app.invoke({"user": "查询 WIDGET-X 库存", "messages": []})
print([t["node"] for t in out["trace"]])""",
                    "首轮轨迹应为 agent、tool、finalize。查询词不含“库存”时不应进 tool。",
                    ["把 user 改成“你好”再跑，轨迹应少哪个节点？", "tool 为什么不要直接 add_edge 回 agent 造成隐式死循环？本课先经过 finalize。"],
                ),
                (
                    6,
                    "Checkpointer 与多轮",
                    "**MemorySaver 按 thread_id 存整份状态。** 同一 `u1` 的第二轮会先 merge 上一轮，再跑新的 user。",
                    "同一 thread 再 invoke 一次",
                    """from agent_lab.graph import MemorySaver
saver = MemorySaver()
app2 = g.compile(checkpointer=saver, recursion_limit=8)
cfg = {"configurable": {"thread_id": "u1"}}
app2.invoke({"user": "查询 WIDGET-X 库存", "messages": []}, cfg)
r2 = app2.invoke({"user": "只是打个招呼", "messages": []}, cfg)
print(r2["messages"])""",
                    "次轮轨迹列表可能仍看得到首轮节点名，因为教学实现里 `trace` 也用 add_messages 累积。这不是 bug，是 reducer 演示。",
                    ["换一个 thread_id 再打招呼，messages 里还应有库存结果吗？", "Checkpointer 若只存最后一条 message，客服场景会丢什么？"],
                ),
                (
                    7,
                    "recursion_limit 熔断",
                    "**图可以合法循环，但不能无限循环。** 自环边 + 很小的 limit 用来上课演示熔断。",
                    "故意造一个炸环",
                    """from agent_lab.graph import StateGraph, START, add_messages
boom = StateGraph({"messages": add_messages})
boom.add_node("loop", lambda s: {"messages": ["x"]})
boom.add_edge(START, "loop")
boom.add_edge("loop", "loop")
try:
    boom.compile(recursion_limit=3).invoke({"messages": []})
except RuntimeError as exc:
    print(exc)""",
                    "真实项目里熔断后应回退到安全回复，而不是让 HTTP 500 漏到用户。本课先要求你能读懂异常字样。",
                    ["limit=3 时节点大约执行几次？", "把 limit 改成 8 却仍自环，验收脚本为什么仍应失败？"],
                ),
                (
                    8,
                    "对照第 15 课",
                    "**OpenClaw 不会另造一套状态哲学。** 它把 session_id 映射为 thread_id，把探活接到同一张图的入口。",
                    "记一句话",
                    """print("LangGraph 状态 -> OpenClawConfig.session_id / timeout / model")""",
                    "本课骨架不会说话也可以验收；下一课才把 Fake 聊天接进 agent 节点。",
                    ["哪些字段你会放进 OpenClawConfig 而不是写进节点闭包？", "为什么 recursion_limit 要出现在 compile 而不是每个节点里？"],
                ),
            ],
            p1_title="构图、多轮、熔断",
            p1s=[
                ("画出闭环", "按案例搭 agent/tool/finalize，invoke 一次库存查询，打印节点轨迹。", "# P1.1: build graph and print first-turn nodes.\n"),
                ("同 thread 第二轮", "对同一 thread_id 再 invoke 一句不含库存的话，打印累积 messages。", "# P1.2: second turn on the same thread_id.\n"),
                ("触发熔断", "自环图 + recursion_limit=3，捕获 RuntimeError 并打印。", "# P1.3: trigger recursion_limit.\n"),
            ],
            close="课后请打开 [chapter14_LangGraph状态图_课后练习.ipynb](chapter14_LangGraph状态图_课后练习.ipynb)。P1 自己解释 reducer，P2 画错一条边并修正，P3 选做隔离两个 thread。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 模块：`agent_lab.graph`。",
            (
                "复现库存闭环并说明 reducer",
                "自行构图：查询 WIDGET-X 库存应经过 tool。打印首轮节点名。用文字说明 `messages` 为何能在第二轮仍看到首轮 think/tool/final。",
                "# P1: graph + first-turn trace + reducer explanation.\n",
                "应交：轨迹；reducer 说明。不要把节点名字改到验收脚本无法辨认还声称“一样”。",
            ),
            (
                "破坏性：漏掉条件边标签",
                "先在 Markdown 写一种错误 mapping（例如没有 `end`），预测异常。再给出修正后的 mapping，并跑一句“只是打个招呼”证明不进 tool。",
                "# P2: greeting path without tool.\n",
                "应交：错误预测；修正证据；打招呼轨迹。故意错误代码留在 Markdown。",
            ),
            (
                "选做：两个 thread 互不污染",
                "thread `a` 查库存，thread `b` 只问好。证明 `b` 的 messages 不含 `WIDGET-X=12`（或说明你如何验证隔离）。",
                "# P3 optional: two thread_ids.\n",
                "若选做，应交：两次 invoke 的 thread_id 与 messages 摘要。",
            ),
        ),
    )

    m = META[2]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="OpenClaw 在本课中的位置：把第 14 课的图和第 13 课的 /v1 收成**可握手的运行时**。评分只看一件事：Client 起来、探活过、首轮状态迁移日志能打印。",
            goals=[
                "写出 OpenClawConfig：Base URL、Key、超时、model、session_id、agent_runtime。",
                "调用 handshake() 得到与阶段零一致的 HealthReport。",
                "run_turn 一次并打印 state_log（turn / node / runtime）。",
                "说明 LangGraph 的 thread_id 如何映射为 session_id。",
            ],
            table="""| 配置 | 握手 | 日志 |
| --- | --- | --- |
| base_url / api_key / timeout_s | probe 同源 | StateTransition |
| model / session_id | report.ok | turn, node, runtime |
| agent_runtime=openclaw | model_ids | 首轮必须非空 |""",
            recap_qs="""1. **R.1** 只 `OpenClawClient()` 却不调用 handshake，算不算“初始化成功”？评分标准怎么写的？
2. **R.2** state_log 里的 runtime 字段从哪来？若拼错成 `open-claw` 会怎样？
3. **R.3** 握手用的端点与 run_turn 用的客户端是否应同源？为什么？""",
            footer_ban="本课不展开 OpenClaw 商业控制台。教学实现见 `agent_lab.openclaw`。",
            sections=[
                (
                    1,
                    "从状态图到运行时配置",
                    "**图是算法，配置是部署。** session_id 对应 Checkpointer 的 thread_id；timeout_s 对应 Http 客户端；model 对应 /v1 的模型名。",
                    "构造一份配置",
                    """from agent_lab.openclaw import OpenClawConfig
cfg = OpenClawConfig(timeout_s=5.0, model="qwen2.5", session_id="handshake-1", agent_runtime="openclaw")
print(cfg.model_dump())""",
                    "Field 上的 description 会进入后续 Prompt/文档。空的 base_url 表示使用阶段零的 Fake。",
                    ["哪些项你会允许学生改，哪些应全班锁定？", "agent_runtime 为什么要出现在日志里而不是只写在注释？"],
                ),
                (
                    2,
                    "Client 初始化",
                    "**初始化 = 读配置 + 取客户端 + 编译图。** 此时还没有和模型握手。",
                    "new 一个 Client",
                    """from agent_lab.openclaw import OpenClawClient, OpenClawConfig
client = OpenClawClient(OpenClawConfig(timeout_s=5.0, session_id="handshake-1"))
print(type(client).__name__, client.source)""",
                    "source 来自 get_client。课堂应为 fake。把它打印出来，避免有人以为已经连上了不存在的 GPU。",
                    ["Client 内部的 MemorySaver 与第 14 课的 saver 是不是同一个类？", "为什么图在 __init__ 里 compile，而不是每次 run_turn 重建？"],
                ),
                (
                    3,
                    "握手探活",
                    "**handshake 直接复用 probe。** 这是任务一 1.1 的硬指标：初始化成功还要探活。",
                    "打印握手",
                    """report = client.handshake()
print(report.ok, report.model_ids, report.source)""",
                    "探活失败时不要继续聊天。评分老师会看这一行是否 ok=True。",
                    ["report 与第 13 课 HealthReport 是否同一模型？", "若真实端点超时，应改 Config.timeout_s 还是在节点里 sleep？"],
                ),
                (
                    4,
                    "首轮状态迁移日志",
                    "**run_turn 把 trace 翻译成 StateTransition 列表。** 字段：turn、node、message、runtime。",
                    "跑一句健康探活",
                    """result = client.run_turn("健康探活")
print(result["state_log"])
print(str(result.get("reply"))[:80])""",
                    "教学图只有 agent 一个节点，所以日志很短。重要的是**有日志且 runtime 为 openclaw**，而不是日志越长越好。",
                    ["message 字段为什么重复了用户输入？便于哪一类对账？", "若 state_log 为空，优先检查哪两个调用？"],
                ),
                (
                    5,
                    "session 与多轮",
                    "**默认 session_id 来自 Config。** 也可以在 run_turn(..., thread_id=) 覆盖，对应 LangGraph configurable.thread_id。",
                    "看返回里的 thread_id",
                    """print(result["thread_id"])""",
                    "客服场景一个用户一个 session。不要把全班作业写进同一个默认 id 还声称互不影响。",
                    ["两个同学都用 lab-session，Checkpointer 在同一进程里会怎样？", "什么时候应该显式传 thread_id？"],
                ),
                (
                    6,
                    "超时与密钥",
                    "**Key 在内网常是占位符，超时不是。** 把它们留在 Config，禁止写进 Prompt。",
                    "读当前超时",
                    """print("timeout_s", client.config.timeout_s)
print("api_key 长度", len(client.config.api_key))""",
                    "打印密钥本身没有教学意义。作业若出现真实 Key，按泄密处理。",
                    ["为什么探活超时和生成超时建议同一配置项？", "Base URL 带不带尾斜杠应由谁 strip？"],
                ),
                (
                    7,
                    "和阶段零对齐",
                    "**同一 Fake，同一 qwen2.5。** OpenClaw 不是第二个模型供应商。",
                    "对照模型名",
                    """print(client.config.model)
print(report.model_ids)""",
                    "若 Config.model 不在列表里，真实 vLLM 会 404。Fake 较宽松，但作业仍应保持一致。",
                    ["列表有 deepseek-r1 时，为何本课默认仍用 qwen2.5？", "换模型名需要改几处配置？"],
                ),
                (
                    8,
                    "10 分评分对照",
                    "**得分点：Client 初始化成功、握手探活、打印首轮状态迁移日志。** 缺日志不得满分。",
                    "自检三件事",
                    """assert report.ok
assert result["state_log"]
assert result["state_log"][0]["runtime"] == "openclaw"
print("1.1 课堂自检通过")""",
                    "experiment.py 就是这三件事的脚本版。讲义综合练习请自己敲，不要复制整文件。",
                    ["runtime 断言失败时，Config 哪一字段写错了？", "只打印 reply 不打印 state_log，会丢哪 10 分里的哪一部分？"],
                ),
            ],
            p1_title="握手 + 首轮日志",
            p1s=[
                ("构造 Client", "写出 OpenClawConfig 与 OpenClawClient，打印 source。", "# P1.1: construct client.\n"),
                ("handshake", "打印 ok、model_ids、source，并确认 ok。", "# P1.2: handshake.\n"),
                ("state_log", "run_turn('健康探活')，打印 state_log，确认 runtime。", "# P1.3: first-turn state_log.\n"),
            ],
            close="课后请打开 [chapter15_OpenClaw运行时_课后练习.ipynb](chapter15_OpenClaw运行时_课后练习.ipynb)。P1 对照 10 分清单，P2 解释配置映射，P3 选做两个 session。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 模块：`agent_lab.openclaw`。",
            (
                "10 分清单跑通",
                "初始化 Client，handshake，run_turn 一次。提交输出中必须出现：report.ok、model_ids、state_log。用表格对照评分标准三句话。",
                "# P1: handshake + state_log.\n",
                "应交：完整输出；三句对照。缺日志视为未完成 1.1。",
            ),
            (
                "映射说明",
                "写一段话：LangGraph 的 thread_id、recursion、/v1 Base URL 分别对应 OpenClawConfig 的哪些字段。不要空泛写“都在配置里”。",
                "# P2: mapping notes (markdown is enough; optional code).\n",
                "应交：至少三对映射。可放 Markdown。",
            ),
            (
                "选做：两个 session",
                "两个 session_id 各 run_turn 一句不同的话，证明 thread_id 出现在结果里且互不相同。",
                "# P3 optional: two sessions.\n",
                "若选做，应交：两个 thread_id 与各自 reply 摘要。",
            ),
        ),
    )


def build_lectures_rest():
    m = META[3]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="模型愿意“配合输出 JSON”不等于字段合法。本课把 JSON Schema 写进 Prompt，再用 Pydantic 当考官。任务一 1.2 按三档给分。",
            goals=[
                "用 BaseModel 与 Field 定义输出模式，并能导出 JSON Schema。",
                "基础：扁平用户信息，手机号去空格且正则通过。",
                "进阶：嵌套工单，状态枚举，total 与明细一致。",
                "高难：自定义 field_validator 归一化脏金额，无法解析则拦截。",
            ],
            table="""| 基础 5分 | 进阶 5分 | 高难 5分 |
| --- | --- | --- |
| UserProfile | TicketAnalysis | DirtyAmount |
| 扁平字段 | 多行商品嵌套 | @field_validator |
| 手机号 11 位 | status 枚举 + total | ￥1,299.00 → 1299.0 |""",
            recap_qs="""1. **R.1** Prompt 里写了“必须 11 位手机号”，模型仍输出带空格的号码。谁负责去空格？
2. **R.2** items 两行金额合计 3297，模型却写 total=3000。应过还是失败？
3. **R.3** 金额字段是“免费送”，校验器应归一成 0 还是 raise？""",
            footer_ban="本课使用 pydantic v2 的 `field_validator` / `model_validator`。不要使用 v1 的 `@validator`。",
            sections=[
                (
                    1,
                    "Schema 注入 Prompt",
                    "**先有结构，再让模型填空。** `model_json_schema()` 可放进 system 消息。模型输出后仍必须 `model_validate`。",
                    "导出一段 Schema",
                    """from agent_lab.schemas import UserProfile
print(list(UserProfile.model_json_schema()["properties"]))""",
                    "Field(description=...) 会出现在 schema 里，等于把注释写给模型看。不要只在中文题面里解释字段。",
                    ["为什么“只在 Prompt 里骂模型要守规矩”不够？", "properties 的键应是字段名还是中文标签？"],
                ),
                (
                    2,
                    "基础：扁平用户",
                    "**单层字段 + 正则。** name / phone / age。phone 允许带空格，校验器去掉后必须是 1 开头 11 位。",
                    "解析一条用户",
                    """from agent_lab.schemas import UserProfile, parse_model
ok, profile = parse_model(UserProfile, {"name": "张三", "phone": "138 0013 8000", "age": 21})
print(ok, profile)""",
                    "parse_model 捕获 ValidationError，返回 (False, exc) 而不是炸内核。这与 Tool 的异常隔离同一哲学。",
                    ["age=-1 会失败在哪个约束？", "phone 写成 1380013800（10 位）应否通过？"],
                ),
                (
                    3,
                    "进阶：嵌套工单",
                    "**LineItem 列表 + status 枚举 + total 交叉检验。** 这是工单明细分析，不是再做一个扁平 dict。",
                    "合法工单",
                    """from agent_lab.schemas import TicketAnalysis, parse_model
payload = {
    "ticket_id": "T-10086",
    "status": "open",
    "items": [
        {"sku": "WIDGET-X", "qty": 2, "price": 1299.0},
        {"sku": "WIDGET-MINI", "qty": 1, "price": 699.0},
    ],
    "total": 3297.0,
}
ok, ticket = parse_model(TicketAnalysis, payload)
print(ok, ticket.total if ok else ticket)""",
                    "2*1299 + 699 = 3297。model_validator 在全部字段就位后比较四舍五入到分。",
                    ["status='OPEN' 能过枚举吗？", "qty=0 为什么应失败？"],
                ),
                (
                    4,
                    "合计不一致",
                    "**进阶档的区分度在交叉校验。** 模型算错 total 时必须失败，不能“差不多就行”。",
                    "故意写错 total",
                    """bad = dict(payload)
bad["total"] = 1.0
ok, err = parse_model(TicketAnalysis, bad)
print(ok)
print(str(err.errors()[0]["msg"])[:60] if not ok else err)""",
                    "客服场景里金额不一致比缺一个逗号更危险。Schema 要拦业务不变量，不只拦类型。",
                    ["若只校验类型不校验合计，漏掉的是哪类事故？", "为什么用 round(..., 2) 再比较？"],
                ),
                (
                    5,
                    "高难：归一化脏金额",
                    "**before 校验器先把字符串变成数。** 去掉 ￥、¥、逗号、元、空格；仍不是数字则 ValueError。",
                    "￥1,299.00",
                    """from agent_lab.schemas import DirtyAmount, parse_model
ok, dirty = parse_model(DirtyAmount, {"amount": "￥1,299.00", "currency": "CNY"})
print(ok, dirty)""",
                    "这是容错，不是放水：能规则化的规则化，不能的必须拦截。",
                    ["mode='after' 时还能处理带 ￥ 的字符串吗？先预测。", "currency 缺省 CNY，传入 'usd' 小写是否本课要标准化？本课不强制。"],
                ),
                (
                    6,
                    "对抗性脏数据",
                    "**“免费送”不得变成 0 元。** 静默成 0 会制造假促销。",
                    "拦截",
                    """ok, bad = parse_model(DirtyAmount, {"amount": "免费送", "currency": "CNY"})
print(ok)
if not ok:
    print(bad.errors()[0]["msg"])""",
                    "高难 5 分同时看两面：能纠偏的纠偏，该拒绝的拒绝。",
                    ["若有人在校验器里 `return 0` 处理一切异常，违反了哪条评分精神？", "空字符串应拦截还是当 0？"],
                ),
                (
                    7,
                    "与模型输出对接",
                    "**Fake 客户端见到“用户信息”“工单”“脏数据”会返回对应 JSON。** 真实模型则依赖你把 schema 塞进 Prompt。",
                    "从聊天拿 JSON 再校验",
                    """import json
from agent_lab.mock_openai import FakeOpenAI
from agent_lab.schemas import UserProfile
raw = FakeOpenAI().chat.completions.create(
    model="qwen2.5",
    messages=[{"role": "user", "content": "请抽取用户信息"}],
)["choices"][0]["message"]["content"]
print(UserProfile.model_validate(json.loads(raw)))""",
                    "课堂 Fake 保证可重复。换真实模型时，失败样例会变多，这正是 Schema 的价值。",
                    ["为什么不让模型直接返回 Python 对象？", "json.loads 失败和 ValidationError 应分成两种日志吗？"],
                ),
                (
                    8,
                    "15 分评分对照",
                    "**三例各 5 分，不能互相替代。** 只会扁平用户最高 5 分。",
                    "三连",
                    """print("基础", parse_model(UserProfile, {"name": "张三", "phone": "13800138000", "age": 21})[0])
print("进阶见 TicketAnalysis")
print("高难见 DirtyAmount 与免费送")""",
                    "experiment.py 四次断言：扁平成功、工单成功、脏金额成功、免费送失败。",
                    ["漏做对抗拦截还能否拿满高难 5 分？", "把校验写在 if 字符串里而不用 Pydantic，是否符合题面？"],
                ),
            ],
            p1_title="三级梯度",
            p1s=[
                ("扁平用户", "解析带空格手机号，打印规范化后的 phone。", "# P1.1: UserProfile.\n"),
                ("嵌套工单", "提交合法工单并打印 total；可选再交一份 total 错误的失败输出。", "# P1.2: TicketAnalysis.\n"),
                ("脏金额", "￥1,299.00 成功；免费送失败。", "# P1.3: DirtyAmount success and reject.\n"),
            ],
            close="课后请打开 [chapter16_Pydantic结构化Prompt_课后练习.ipynb](chapter16_Pydantic结构化Prompt_课后练习.ipynb)。P1 基础、P2 进阶、P3 选做自己写一个校验器。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 模块：`agent_lab.schemas`。",
            (
                "基础用例：用户信息规范化",
                "使用 `UserProfile` 解析至少一条带空格或混杂格式的手机号。打印规范化结果。再给一条非法手机号，证明会被拦截。",
                "# P1: UserProfile success + reject.\n",
                "应交：成功实例；失败实例；phone 规则用自己的话复述。",
            ),
            (
                "进阶用例：工单明细",
                "构造不少于两行商品的工单，status 使用枚举值，total 必须与明细一致。另外构造 total 不一致的一份，展示错误信息。",
                "# P2: nested ticket ok + total mismatch.\n",
                "应交：成功 total；失败消息。不要手工改算术却把错误 total 写成正确值。",
            ),
            (
                "选做：自己的 field_validator",
                "新写一个极小 BaseModel（不要抄 DirtyAmount 字段名），对某一字段做归一化或拒绝。说明规则。",
                "# P3 optional: your own validator.\n",
                "若选做，应交：模型代码、一正一反两个例子。",
            ),
        ),
    )

    m = META[4]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="有了 Schema 还不够：模型要能**调用工具**。本课先做带契约的本地 Tool，再演示 MCP 握手与能力发现。任务二 2.1 占 10 分，2.2 占 5 分。",
            goals=[
                "用 ArgsSchema 与 ResultSchema 定义 Tool 契约。",
                "执行逻辑隔离异常：返回 ok=False 与 error 文本，不中断程序。",
                "导出 Function Calling Schema。",
                "MCP Client 握手并列出远程（教学为进程内）Tools 与 Resources。",
            ],
            table="""| Tool 10分 | MCP 5分 |
| --- | --- |
| Args / Result | handshake ok |
| export_function_schema | tools 元数据 |
| 校验失败不崩溃 | resources 清单 |""",
            recap_qs="""1. **R.1** sku='x' 长度不足，应 raise 还是返回 ok=False？
2. **R.2** Function Calling 的 parameters 从哪份 Schema 来？
3. **R.3** 握手成功是否等于已经执行了 kb_lookup？""",
            footer_ban="教学 MCP 在进程内模拟 stdio 握手，避免课堂依赖外部 npx 进程。概念上仍区分 Client / Server。",
            sections=[
                (
                    1,
                    "契约：Args 与 Result",
                    "**入参、出参都是 BaseModel。** 库存工具：sku 最短 3 字符；结果带 stock 与 ok/error。",
                    "看库存表",
                    """from agent_lab.tools import STOCK, InventoryArgs, InventoryResult
print(STOCK)
print(InventoryArgs.model_json_schema()["properties"])""",
                    "WIDGET-X 库存 12，WIDGET-MINI 库存 4。未知 SKU 是业务失败，不是 Python 异常。",
                    ["为什么 Result 也要 Schema，而不是随便 return dict？", "min_length=3 拦的是哪类胡言？"],
                ),
                (
                    2,
                    "导出 Function Calling Schema",
                    "**给模型看的是 JSON，不是 Python 类。** `export_function_schema` 包一层 type=function。",
                    "导出",
                    """import json
from agent_lab.tools import inventory_tool
print(json.dumps(inventory_tool.export_function_schema(), ensure_ascii=False, indent=2)[:400])""",
                    "评分老师会看 name 是否为 inventory_lookup，以及 parameters 是否含 sku。",
                    ["description 空着会有什么后果？", "为什么 parameters 用 args_schema.model_json_schema()？"],
                ),
                (
                    3,
                    "正常调用",
                    "**run() 先 validate 再执行。**",
                    "查 WIDGET-X",
                    """good = inventory_tool.run(sku="WIDGET-X")
print(good)""",
                    "stock 必须是 12。不要在作业里重新发明另一张库存表还声称同一验收。",
                    ["sku 大小写不统一时应否在工具内部归一？本课 lookup 会 upper。", "run 的返回值类型是 BaseModel 还是 dict？"],
                ),
                (
                    4,
                    "参数校验隔离",
                    "**太短的 sku 不得让 Jupyter 停在 Traceback。**",
                    "sku='x'",
                    """isolated = inventory_tool.run(sku="x")
print(isolated.ok, isolated.error)""",
                    "error 来自 Pydantic 的第一条 msg。程序继续，Agent 才能把错误喂回模型。",
                    ["若 Tool.run 直接 raise，Self-Correction 还做不做得到？", "空 sku 与未知 sku 是同一类失败吗？"],
                ),
                (
                    5,
                    "业务异常隔离",
                    "**未知 SKU 走业务分支。** ok=False，error='未知 SKU'。",
                    "UNKNOWN-SKU",
                    """unknown = inventory_tool.run(sku="UNKNOWN-SKU")
print(unknown.ok, unknown.error, unknown.stock)""",
                    "stock=0 且 ok=False。不要只看数字 0，免费商品也可能是 0 库存。",
                    ["为什么未知 SKU 不直接 ValidationError？", "隔离的“标准错误文本”会在第 18 课自愈时用到，指的是哪一字段？"],
                ),
                (
                    6,
                    "MCP 握手模型",
                    "**Client 与 Server 先握手，再发现能力。** 传输可以是 stdio 或 SSE。本课教学实现 transport='stdio'。",
                    "握手",
                    """from agent_lab.mcp import MCPClient
hs = MCPClient(transport="stdio").handshake()
print(hs.ok, hs.protocol, hs.server)""",
                    "server 名为 lab-mcp。真实项目里这一步还会交换协议版本。",
                    ["stdio 和 SSE 对“谁启动谁”的直觉差别是什么？", "handshake 返回的是元数据还是工具执行结果？"],
                ),
                (
                    7,
                    "能力发现",
                    "**列出 Tools 与 Resources。** 本课要求完整读取清单，不要求真的调 kb_lookup。",
                    "打印清单",
                    """print([t.name for t in hs.tools])
print([r.uri for r in hs.resources])""",
                    "应看到 kb_lookup、echo_time 与 kb://manual、kb://policy。5 分就给在这份清单上。",
                    ["Resource 的 mime_type 有什么用？", "为什么发现与调用要分成两步？"],
                ),
                (
                    8,
                    "15 分评分对照",
                    "**2.1 与 2.2 分开给分。** 只会 MCP 不会写 Tool 拿不到 10 分。",
                    "自检",
                    """assert good.ok and good.stock == 12
assert isolated.ok is False
assert hs.ok and len(hs.tools) >= 2
print("2.1+2.2 课堂自检通过")""",
                    "下一课把这些 Tool 收成 Skill，MCP 工具也可以被组合进去。",
                    ["export 缺少 parameters 时 2.1 能否满分？", "只握手成功但 tools 为空，2.2 能否满分？"],
                ),
            ],
            p1_title="Tool + MCP",
            p1s=[
                ("导出 Schema 并正常调用", "打印 function name 与 properties，run WIDGET-X。", "# P1.1: schema + happy path.\n"),
                ("两类隔离", "短 sku 与未知 sku 都不得崩溃，打印 ok 与 error。", "# P1.2: isolation.\n"),
                ("MCP 清单", "handshake 后列出 tools 与 resources。", "# P1.3: MCP metadata.\n"),
            ],
            close="课后请打开 [chapter17_自定义Tool与MCP_课后练习.ipynb](chapter17_自定义Tool与MCP_课后练习.ipynb)。P1 写清契约，P2 做 MCP 发现，P3 选做一枚新 Tool。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 模块：`agent_lab.tools`、`agent_lab.mcp`。",
            (
                "独立 Tool 契约与隔离",
                "导出 inventory_lookup 的 Function Calling Schema。展示：正常库存、参数校验失败、业务未知 SKU。强调三次调用都没有让程序中断。",
                "# P1: tool schema + three runs.\n",
                "应交：schema 关键字段；三次 Result；一句话说明隔离策略。",
            ),
            (
                "MCP 能力发现",
                "完成握手，完整打印 tools（name/description）与 resources（uri/name）。说明握手成功 ≠ 已经检索了知识库。",
                "# P2: MCP handshake metadata.\n",
                "应交：清单；协议名 stdio；概念说明。",
            ),
            (
                "选做：再封装一枚 Tool",
                "用现成的 `Tool` 类包装 `total_tool` 或你自己的加法逻辑，展示一次校验失败。不要修改 agent_lab 源码，笔记本内完成即可。",
                "# P3 optional: another tool.\n",
                "若选做，应交：schema、一次成功、一次失败。",
            ),
        ),
    )

    m = META[5]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="Skill 是业务动词：报价、下单、检索。它内部可以串起多个 Tool，并在失败时把错误变成下一轮输入。任务二 2.3 共 20 分。",
            goals=[
                "基础：模型意图命中正确 Skill，入参符合 Pydantic。",
                "进阶：Tool A 产出经校验后注入 Tool B。",
                "高难：模糊指令先失败，再 Self-Correction 成功。",
            ],
            table="""| 基础 6分 | 进阶 7分 | 高难 7分 |
| --- | --- | --- |
| 单工具精准命中 | 串行双工具 | 入参错误自愈 |
| WIDGET-X qty=1 | MINI qty=2 total=1398 | 小部件X → WIDGET-X |""",
            recap_qs="""1. **R.1** 用户说“查一下 WIDGET-X 报价”，应调用 Skill 还是直接拼字符串？
2. **R.2** 库存工具返回的 sku 为什么要作为计价工具的输入，而不是重新从用户句子里抠？
3. **R.3** 自愈若第一轮就已经用别名成功，attempts 应是 1 还是 2？本课高难要求什么？""",
            footer_ban="库存与单价以教学常量为准：X 价 1299 库存 12，MINI 价 699 库存 4。",
            sections=[
                (
                    1,
                    "Skill 是组合",
                    "**Tool 做一件原子事，Skill 完成一笔业务。** quote_skill = 查库存 + 算金额。",
                    "看函数签名",
                    """from agent_lab.skills import quote_skill, self_correct_quote, normalize_sku
print("normalize_sku('小部件X') ->", normalize_sku("小部件X"))""",
                    "别名表是教学用的最小清洗。真实项目会放在商品主数据，而不是写死在 Skill 里。",
                    ["把别名清洗放在 Tool 内或 Skill 内各有何利弊？", "MCP 的 kb_lookup 能否成为某个 Skill 的一步？"],
                ),
                (
                    2,
                    "基础：单工具精准命中",
                    "**入参完全符合规范：WIDGET-X、qty=1、price=1299。** 库存 12，total=1299。",
                    "命中",
                    """basic = quote_skill("WIDGET-X", qty=1, price=1299)
print(basic)
assert basic["ok"] and basic["sku"] == "WIDGET-X" """,
                    "6 分看的是意图到正确 SKU，而不是把所有输入都模糊匹配成功。",
                    ["qty 与 price 为何仍要 Pydantic？", "若模型把 MINI 说成 X，基础用例应否“聪明地改掉”？"],
                ),
                (
                    3,
                    "进阶：双工具流转",
                    "**A 的输出经过校验，再进 B。** 库存 ok 后才 calc_total。MINI×2×699=1398。",
                    "串行",
                    """chained = quote_skill("WIDGET-MINI", qty=2, price=699)
print(chained)
assert chained["ok"] and chained["total"] == 1398.0""",
                    "不要在第二步重新输入用户的原始字符串。要用清洗后的 sku、qty、price。",
                    ["若库存失败仍去计价，会制造什么假报表？", "total 为什么不要在 Skill 里用 qty*price 自己乘一遍绕过 total_tool？本课要求走工具。"],
                ),
                (
                    4,
                    "数据清洗点",
                    "**每一次跨工具都是 Schema 边界。** 非法 qty 应在 TotalArgs 失败，而不是算出负数。",
                    "看失败形态（参数）",
                    """from agent_lab.tools import total_tool
print(total_tool.run(qty=0, price=10))""",
                    "Skill 要把这类 error 原样带到 QuoteResult.error，供下一轮模型阅读。",
                    ["清洗发生在 Skill 还是 Tool？本课两处都有，如何分工？", "为什么 Result 同时保留 ok 与 error 空串？"],
                ),
                (
                    5,
                    "高难：先失败",
                    "**人为制造模糊指令。** “帮我查一下小部件X的库存报价” 不是合法 SKU。allow_repair=False 时必须失败。",
                    "第一轮",
                    """first = quote_skill("帮我查一下小部件X的库存报价", qty=2, price=1299, allow_repair=False)
print(first["ok"], first["error"])""",
                    "first_error 应接近“未知 SKU”。没有这轮失败，自愈就变成普通别名，拿不到高难 7 分。",
                    ["为何不在第一轮就 normalize？", "用户句子里混着“帮我查一下”对 Args.sku 的 min_length 意味着什么？"],
                ),
                (
                    6,
                    "Self-Correction",
                    "**捕获错误原因，下一轮修正调用。** self_correct_quote 固定演示 attempts=2, repaired=True。",
                    "第二轮",
                    """repaired = self_correct_quote("帮我查一下小部件X的库存报价")
print(repaired)
assert repaired["ok"] and repaired["repaired"] is True and repaired["attempts"] == 2""",
                    "qty 默认 2，price 默认 1299，总价 2598。这是教学约定，作业不要改常量还说“也对”。",
                    ["Agent 要把 first_error 放进下一轮 Prompt 的哪一角色消息里更合理？", "修正后仍失败应停止还是无限重试？对照 recursion_limit。"],
                ),
                (
                    7,
                    "状态保持",
                    "**链式调用中的中间值要显式入状态。** 本课用返回 dict；第 14 课的 messages reducer 是同一思想。",
                    "中间字段",
                    """print({k: repaired[k] for k in ["sku", "stock", "qty", "total", "first_error"]})""",
                    "评分时看这些字段是否对得上，而不是只看 ok=True。",
                    ["stock 来自哪一个 Tool？", "first_error 在成功后为何仍保留？"],
                ),
                (
                    8,
                    "20 分评分对照",
                    "**6+7+7，三档都要交证据。**",
                    "三连打印",
                    """print("basic", basic["total"])
print("chained", chained["total"])
print("repaired", repaired["sku"], repaired["attempts"])""",
                    "experiment.py 即此三连。综合练习请分格写。",
                    ["只做自愈不做双工具，最高多少分？", "把 attempts 写死为 2 而不调用两轮，算不算造假？"],
                ),
            ],
            p1_title="三级 Skill",
            p1s=[
                ("基础命中", "quote_skill WIDGET-X qty=1 price=1299，打印结果。", "# P1.1: basic hit.\n"),
                ("双工具", "WIDGET-MINI qty=2 price=699，确认 total=1398。", "# P1.2: chained tools.\n"),
                ("自愈", "self_correct_quote 模糊中文，确认 repaired 与 attempts。", "# P1.3: self-correct.\n"),
            ],
            close="课后请打开 [chapter18_Skill封装与链式联动_课后练习.ipynb](chapter18_Skill封装与链式联动_课后练习.ipynb)。P1 基础、P2 进阶、P3 选做分析 first_error。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 模块：`agent_lab.skills`。库存常量不要改。",
            (
                "基础：单工具命中",
                "给出一句明确意图（SKU 合法），调用 quote_skill，证明 sku/stock/total 符合 Pydantic 结果。说明为什么这算“精准命中”。",
                "# P1: precise skill hit.\n",
                "应交：入参、出参、一句话意图说明。",
            ),
            (
                "进阶：串行双工具",
                "MINI 两件。用文字画出 Tool A → 校验 → Tool B。打印 total=1398.0。指出你没有在 Skill 外手算后写死。",
                "# P2: A then B.\n",
                "应交：流程图（可用文字箭头）；运行输出。",
            ),
            (
                "选做：自愈过程记录",
                "运行 self_correct_quote，对照 first_error 与最终 sku。若你另写一轮“先失败再 normalize”也可，但必须能看出两轮。",
                "# P3 optional: self-correction trace.\n",
                "若选做，应交：attempts、first_error、最终 total。",
            ),
        ),
    )

    m = META[6]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="模型没有读过你们公司的手册。RAG 把文档切片、向量化（本课用词频向量教学）、入库，再把 Retriever 当成 Skill/Tool 给 Agent 按需调用。任务三 3.1 占 15 分。",
            goals=[
                "按段落做 Chunking，生成 chunk_id。",
                "构建 Retriever，对续航类问题命中产品手册。",
                "把检索封装为标准 Tool 并成功调用。",
            ],
            table="""| 分块 | 入库 | 调用 |
| --- | --- | --- |
| 按空行近似 80 字 | TF 向量 + 检索 | rag_search Tool |
| doc_id::idx | 命中 hits | ResultSchema.hits |""",
            recap_qs="""1. **R.1** 把三份 md 全文塞进 system Prompt，手册变厚时会怎样？
2. **R.2** chunk_id 写成 0、1、2 全局自增，跨文档溯源时有何不便？
3. **R.3** Agent 不调用 Retriever 直接回答续航，算不算 3.1 通过？""",
            footer_ban="教学检索不连云端 Embedding API。中文用汉字 unigram/bigram 分词。知识库副本在本课 `kb/`。",
            sections=[
                (
                    1,
                    "流水线全景",
                    "**文档 → 切片 → 索引 → 查询 → 命中文本。** Agent 只在需要时调用最后一步。",
                    "加载语料",
                    """from pathlib import Path
from agent_lab.rag import load_corpus, Retriever
KB = Path.cwd().parent / "agent_lab" / "knowledge"
chunks = load_corpus(KB)
print(len(chunks), [c.chunk_id for c in chunks])""",
                    "应看到 manual / price / policy 的若干 chunk。条数过少说明没读到 md。",
                    ["为何按空行切而不是按固定 10 个汉字切？课堂选择的代价是什么？", "policy 与续航问题无关时仍入库，对吗？"],
                ),
                (
                    2,
                    "Chunking",
                    "**每块要能独立引用。** chunk_id = doc_id + 序号。",
                    "看第一块",
                    """print(chunks[0].model_dump())""",
                    "后文溯源必须带回这段 id，而不是“根据网上资料”。",
                    ["同一文档第二段的 id 应如何递增？", "切得太碎或太长各有什么检索后果？"],
                ),
                (
                    3,
                    "向量化（教学版）",
                    "**本课用词频向量 + 余弦，外加 BM25 备着第 20 课。** 不是工业 Embedding，但接口一样：query in，hits out。",
                    "检索续航",
                    """retriever = Retriever(chunks)
hits = retriever.search("Widget-X 续航", k=3)
for h in hits:
    print(h.score, h.chunk_id, h.text[:40])""",
                    "第一条应落在手册续航附近。若落到价格表，检查分词是否把中文拆没了。",
                    ["k=3 的吞吐含义是什么？", "score 跨查询能直接比大小吗？"],
                ),
                (
                    4,
                    "封装为 Tool",
                    "**Retriever 对 Agent 来说只是又一枚 Tool。** Args=query，Result=hits。",
                    "挂载",
                    """from pydantic import BaseModel, Field
from agent_lab.tools import Tool

class SearchArgs(BaseModel):
    query: str = Field(min_length=2)

class SearchResult(BaseModel):
    ok: bool = True
    error: str = ""
    hits: list = Field(default_factory=list)

def _search(args: SearchArgs):
    found = retriever.search(args.query, k=3)
    return {"ok": True, "error": "", "hits": [h.model_dump() for h in found]}

rag_tool = Tool("rag_search", "从产品知识库检索", SearchArgs, SearchResult, _search)
result = rag_tool.run(query="Widget-X 续航")
print(result.ok, result.hits[0]["chunk_id"])""",
                    "15 分要求：独立服务可用（本课即 Retriever 对象）且成功被这种调用碰到。",
                    ["query 一个字为何要失败？", "hits 放进 ResultSchema 而不是 print，是为了谁？"],
                ),
                (
                    5,
                    "命中率抽检",
                    "**续航问题必须能在 hits 文本里看到续航或 48。**",
                    "断言思路",
                    """assert result.ok and result.hits
assert any("续航" in h["text"] or "48" in h["text"] for h in result.hits)
print("抽检通过")""",
                    "课堂知识库很小，抽检不是刷榜。换自己的文档后要重新选探针问题。",
                    ["只用英文 Widget-X 不写续航，还保证命中手册吗？", "命中价格表算不算本探针失败？"],
                ),
                (
                    6,
                    "给 Agent 按需调用",
                    "**不是每轮都检索。** 问候语不必查库；事实型产品问题才调用 rag_search。对照第 14 课 need_tool。",
                    "意图粗分",
                    """def need_rag(text):
    keys = ["续航", "价格", "质保", "Widget"]
    return any(k in text for k in keys)
print(need_rag("你好"), need_rag("Widget-X 续航多久"))""",
                    "真实系统会用更稳的路由。本课只要你意识到 Retriever 是节点上的工具。",
                    ["无条件每轮检索的坏处？", "检索结果要不要再进 Pydantic SourcedAnswer？第 20 课做。"],
                ),
                (
                    7,
                    "本课 kb/ 副本",
                    "**课后独立读取本课 kb/，避免讲义变量残留。** 内容与 agent_lab/knowledge 一致。",
                    "列出本课 kb",
                    """from pathlib import Path
print(sorted(p.name for p in Path("kb").glob("*.md")))""",
                    "三份：manual.md / price.md / policy.md。不要上网另下语料。",
                    ["验收脚本读的是哪套路径？", "你改了 kb 但没改 agent_lab/knowledge，experiment.py 会变吗？"],
                ),
                (
                    8,
                    "15 分评分对照",
                    "**流水线可用 + Agent 调用 + 探针命中。**",
                    "回顾三项",
                    """print("chunks", len(chunks))
print("tool", rag_tool.name)
print("hit0", result.hits[0]["chunk_id"])""",
                    "调优、混合检索、幻觉兜底留给第 20 课，本课不要提前把 fallback 当主线。",
                    ["没有 Tool 封装、只在笔记本 print hits，会缺哪条评分？", "吞吐在本课如何体现（k 路检索）？"],
                ),
            ],
            p1_title="检索服务挂到 Tool",
            p1s=[
                ("分块", "load_corpus，打印分块数与前三个 chunk_id。", "# P1.1: chunking.\n"),
                ("检索", "查询 Widget-X 续航，打印 top hits。", "# P1.2: search.\n"),
                ("Tool 调用", "封装 rag_search 并 run，确认命中续航或 48。", "# P1.3: retriever as tool.\n"),
            ],
            close="课后请打开 [chapter19_RAG检索流水线_课后练习.ipynb](chapter19_RAG检索流水线_课后练习.ipynb)，读取本课 [kb/](kb)。P1 自己建索引，P2 封装 Tool，P3 选做另一探针。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 请读取本课 `kb/*.md`。可用 `load_corpus(Path('kb'))`。",
            (
                "从 kb/ 重建流水线",
                "不要使用讲义里可能残留的 chunks 变量。重新 load、打印每个 doc_id 的块数。查询“续航”，展示命中文本。",
                "# P1: rebuild retriever from ./kb.\n",
                "应交：块数；top hit 的 chunk_id 与摘录。",
            ),
            (
                "Retriever 作为 Tool",
                "在笔记本内定义 SearchArgs / SearchResult，用 `Tool` 包装 search。用一次 Agent 风格的 run(query=...) 调用。",
                "# P2: wrap as tool.\n",
                "应交：tool name；Result；说明这算被 Agent 调用的最小形态。",
            ),
            (
                "选做：第二条探针",
                "再查一个知识库内问题（如质保年限或 Mini 售价），记录是否命中对应文档。",
                "# P3 optional: second probe.\n",
                "若选做，应交：问题、chunk_id、是否符合预期。",
            ),
        ),
    )

    m = META[7]
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_学生讲义.ipynb" % (m["num"], m["theme"])),
        lecture_shell(
            m,
            recap="检索能用之后要**准**、要**可追溯**、要**会拒绝**。任务三 3.2 共 25 分：单文档 7、跨文档 9、越界兜底 9。",
            goals=[
                "说明混合检索（余弦 + BM25）与截断重排。",
                "用 SourcedAnswer 强制携带 chunk_id、置信度、原文片段。",
                "对知识库外问题返回 FallbackResponse，而不是幻觉。",
            ],
            table="""| 基础 7分 | 进阶 9分 | 高难 9分 |
| --- | --- | --- |
| 单文档事实 | 跨文档对比 | 越界 / 幻觉对抗 |
| 带 sources | 至少两个 doc_id | kind=fallback |""",
            recap_qs="""1. **R.1** 只向量或只 BM25，短中文查询可能怎样？
2. **R.2** 回答很对但没有 chunk_id，本课算不算合格溯源？
3. **R.3** “明天深圳天气怎么样？”应走哪一种实体？""",
            footer_ban="OUT_OF_CORPUS 关键词含天气、股价、中奖等。不要把兜底做成“我猜可能下雨”。",
            sections=[
                (
                    1,
                    "混合检索",
                    "**余弦捕捉重叠词，BM25 惩罚过长块、奖励罕见词。** 本课 0.6 * cosine + 0.4 * bm25。",
                    "打开检索",
                    """from pathlib import Path
from agent_lab.rag import Retriever, load_corpus, answer_with_rag
KB = Path.cwd().parent / "agent_lab" / "knowledge"
retriever = Retriever(load_corpus(KB))
for h in retriever.search("对比价格与续航", k=3, hybrid=True):
    print(h.score, h.chunk_id)""",
                    "hybrid=False 可对照。作业要能说出一句话差异，不要求调参比赛。",
                    ["b 参数与文档长度有何关系（直觉即可）？", "为什么重排先取 2k 再截回 k？本课是教学截断。"],
                ),
                (
                    2,
                    "结构化溯源",
                    "**SourcedAnswer.sources 每项含 chunk_id、confidence、quote。**",
                    "看模型",
                    """from agent_lab.rag import SourcedAnswer, FallbackResponse
print(SourcedAnswer.model_json_schema()["properties"].keys())
print(FallbackResponse.model_json_schema()["properties"].keys())""",
                    "两种实体用 kind 区分：answer 或 fallback。不要混成一个随便 dict。",
                    ["confidence 在教学里等于检索 score，工业上还可能来自 Rerank 模型。差别？", "quote 截到 80 字是为了什么？"],
                ),
                (
                    3,
                    "基础：单文档精准定位",
                    "**事实型：Widget-X 续航多久？** 应引用手册切片。",
                    "基础",
                    """basic = answer_with_rag(retriever, "Widget-X 续航多久？")
print(basic["kind"], basic.get("sources", [{}])[0].get("chunk_id"))
print(basic["answer"][:80])""",
                    "7 分看格式规整 + 来源切片，不看文采。",
                    ["若 sources 为空但 answer 很长，如何判？", "chunk_id 应以 manual 为主还是 price？"],
                ),
                (
                    4,
                    "进阶：跨文档聚合",
                    "**价格在 price.md，续航在 manual.md。** 对比题必须两边都出现在 sources 的 doc_id 集合里。",
                    "对比",
                    """advanced = answer_with_rag(retriever, "对比 Widget-X 和 Widget-Mini 的价格与续航")
print([s["chunk_id"] for s in advanced.get("sources", [])])
print({s["chunk_id"].split("::")[0] for s in advanced["sources"]})""",
                    "可用 Markdown 表在作业里手工整理对比，但数据必须来自 hits，禁止凭记忆填 1299。",
                    ["不相连片段指的是什么？", "只有 price::0 三条重复算不算跨文档？"],
                ),
                (
                    5,
                    "高难：越界提问",
                    "**知识库外必须拒绝编造。** 天气触发 out_of_corpus。",
                    "天气",
                    """hard = answer_with_rag(retriever, "明天深圳天气怎么样？")
print(hard)
assert hard["kind"] == "fallback" """,
                    "FallbackResponse 含 reason、message、question。这是防御，不是答非所问。",
                    ["若去掉关键词列表、只靠 score<0.05，天气题还稳吗？对照教学实现。", "把天气编成“小雨转晴”会在哪一档零分？"],
                ),
                (
                    6,
                    "低置信兜底",
                    "**库内但分数过低也会 fallback。** reason=low_confidence。",
                    "读阈值",
                    """print("hits[0].score < 0.05 -> low_confidence")""",
                    "阈值是教学常数。作业解释它的存在即可，不必网格搜索。",
                    ["阈过高会怎样？过低会怎样？", "与越界关键词防御如何叠加？"],
                ),
                (
                    7,
                    "幻觉对抗清单",
                    "**对抗不是攻击学校，是验收。** 准备：库内事实、跨库对比、库外诱导。",
                    "三类问题",
                    """probes = ["Widget-X 续航多久？", "对比 Widget-X 和 Widget-Mini 的价格与续航", "明天深圳天气怎么样？"]
for q in probes:
    a = answer_with_rag(retriever, q)
    print(q, "->", a["kind"], a.get("reason"))""",
                    "学期收束：Serving 约束输出、图约束流程、Schema 约束字段、RAG 约束证据。",
                    ["哪一层防的是“说得像真的”？", "哪一层防的是“无限循环”？"],
                ),
                (
                    8,
                    "25 分评分对照",
                    "**7+9+9。** experiment.py 三连断言。",
                    "自检",
                    """assert basic["kind"] == "answer" and basic["sources"]
assert len({s["chunk_id"].split("::")[0] for s in advanced["sources"]}) >= 2
assert hard["reason"] == "out_of_corpus"
print("3.2 课堂自检通过")""",
                    "完成后运行本课 experiment.py。不要改知识库来让天气变成手册内容。",
                    ["跨文档不足两个 doc_id 扣哪 9 分？", "fallback 的 message 需要文学性吗？"],
                ),
            ],
            p1_title="溯源与兜底",
            p1s=[
                ("单文档", "提问续航，打印 answer 与 sources。", "# P1.1: single-doc sourced answer.\n"),
                ("跨文档", "对比价格与续航，列出 doc_id 集合。", "# P1.2: multi-doc sources.\n"),
                ("越界", "天气问题必须 kind=fallback。", "# P1.3: fallback.\n"),
            ],
            close="课后请打开 [chapter20_RAG调优与结构化溯源_课后练习.ipynb](chapter20_RAG调优与结构化溯源_课后练习.ipynb)。P1 基础、P2 进阶对比表、P3 选做再写一个越界问题。本模块到此收束。",
        ),
    )
    dump_nb(
        ROOT / m["folder"] / ("chapter%s_%s_课后练习.ipynb" % (m["num"], m["theme"])),
        hw_shell(
            m,
            m["hw_extra"] + " 读取 `kb/` 或 `agent_lab/knowledge`，需在报告中写明路径。",
            (
                "基础：单文档 + 溯源",
                "对事实型问题作答。输出必须能被理解为 SourcedAnswer：有 answer，有至少一条含 chunk_id、confidence、quote 的来源。格式规整。",
                "# P1: sourced factoid.\n",
                "应交：问题、结构化输出。不要只交一段无出处散文。",
            ),
            (
                "进阶：跨文档对比表",
                "对比 Widget-X 与 Widget-Mini 的价格与续航。用 Markdown 表整理，单元格数字/事实必须能在 sources 的 quote 中找到。doc_id 不少于两个。",
                "# P2: comparison table from multiple chunks.\n",
                "应交：表；sources 列表；说明片段不必在原文中相邻。",
            ),
            (
                "选做：另一越界题",
                "除天气外再选股价/彩票等 OUT_OF_CORPUS 方向，证明仍返回 FallbackResponse。解释为何不能靠模型礼貌拒绝代替该实体。",
                "# P3 optional: another out-of-corpus probe.\n",
                "若选做，应交：问题、fallback JSON、理由。",
            ),
        ),
    )


def update_indexes():
    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    if "第13课-模型私有化部署与Serving" not in text:
        extra = """
## 后续模块：Agent 实训（第13–20课）

前 12 课材料不变。第 13 课起进入私有化模型与 Agent，共用 [`agent_lab/`](agent_lab/README.md)。大纲见 [`教学内容大纲-Agent.md`](教学内容大纲-Agent.md)，课表见 [`后续Agent课程安排.md`](后续Agent课程安排.md)。

| 文件夹 | 当堂主实验 | 数据 / 运行时 |
|--------|------------|----------------|
| [第13课-模型私有化部署与Serving](第13课-模型私有化部署与Serving) | 讲义 `chapter13_模型私有化部署与Serving_学生讲义.ipynb` / 课后 `chapter13_模型私有化部署与Serving_课后练习.ipynb` / 验收 `experiment.py` | `agent_lab`；可选 `serving.env.example` |
| [第14课-LangGraph状态图与Agent骨架](第14课-LangGraph状态图与Agent骨架) | 讲义 `chapter14_LangGraph状态图_学生讲义.ipynb` / 课后 `chapter14_LangGraph状态图_课后练习.ipynb` / 验收 `experiment.py` | `agent_lab.graph` |
| [第15课-OpenClaw运行时初始化](第15课-OpenClaw运行时初始化) | 讲义 `chapter15_OpenClaw运行时_学生讲义.ipynb` / 课后 `chapter15_OpenClaw运行时_课后练习.ipynb` / 验收 `experiment.py` | 任务一 1.1 / 10分 |
| [第16课-Pydantic结构化Prompt](第16课-Pydantic结构化Prompt) | 讲义 `chapter16_Pydantic结构化Prompt_学生讲义.ipynb` / 课后 `chapter16_Pydantic结构化Prompt_课后练习.ipynb` / 验收 `experiment.py` | 任务一 1.2 / 15分 |
| [第17课-自定义Tool与MCP接入](第17课-自定义Tool与MCP接入) | 讲义 `chapter17_自定义Tool与MCP_学生讲义.ipynb` / 课后 `chapter17_自定义Tool与MCP_课后练习.ipynb` / 验收 `experiment.py` | 任务二 2.1+2.2 / 15分 |
| [第18课-Skill封装与链式联动](第18课-Skill封装与链式联动) | 讲义 `chapter18_Skill封装与链式联动_学生讲义.ipynb` / 课后 `chapter18_Skill封装与链式联动_课后练习.ipynb` / 验收 `experiment.py` | 任务二 2.3 / 20分 |
| [第19课-RAG检索流水线](第19课-RAG检索流水线) | 讲义 `chapter19_RAG检索流水线_学生讲义.ipynb` / 课后 `chapter19_RAG检索流水线_课后练习.ipynb` / 验收 `experiment.py` | `kb/`；任务三 3.1 / 15分 |
| [第20课-RAG调优与结构化溯源](第20课-RAG调优与结构化溯源) | 讲义 `chapter20_RAG调优与结构化溯源_学生讲义.ipynb` / 课后 `chapter20_RAG调优与结构化溯源_课后练习.ipynb` / 验收 `experiment.py` | `kb/`；任务三 3.2 / 25分 |

批量自测仍使用 `python3 运行全部实验.py`（现含第 1–20 课）。Agent 课未配置 GPU 时走 Fake `/v1`。
"""
        text = text.replace("本目录是开课用的 **12 节课材料包**。", "本目录是开课用的 **12 节 Python 数据分析课**，外加 **8 节 Agent 实训课**（第13–20课）。")
        text = text.replace("第 3–12 课讲义为 `chapterXX_*_学生讲义.ipynb`，课后作业为 `chapterXX_*_课后练习.ipynb`。`experiment.py` 是已填好的验收版。", "第 3–20 课讲义为 `chapterXX_*_学生讲义.ipynb`，课后作业为 `chapterXX_*_课后练习.ipynb`。`experiment.py` 是已填好的验收版。")
        text = text.rstrip() + "\n" + extra
        readme_path.write_text(text, encoding="utf-8")

    runner = ROOT / "运行全部实验.py"
    src = runner.read_text(encoding="utf-8")
    if "第13课-模型私有化部署与Serving" not in src:
        src = src.replace(
            '    "第12课-模块与日期时间",\n]',
            """    "第12课-模块与日期时间",
    "第13课-模型私有化部署与Serving",
    "第14课-LangGraph状态图与Agent骨架",
    "第15课-OpenClaw运行时初始化",
    "第16课-Pydantic结构化Prompt",
    "第17课-自定义Tool与MCP接入",
    "第18课-Skill封装与链式联动",
    "第19课-RAG检索流水线",
    "第20课-RAG调优与结构化溯源",
]""",
        )
        runner.write_text(src, encoding="utf-8")

    outline = ROOT / "教学内容大纲.md"
    ot = outline.read_text(encoding="utf-8")
    if "第13–20课" not in ot and "后续模块：Agent" not in ot:
        ot = ot.rstrip() + """

---

## 6. 后续模块（第13–20课，不改前 12 课边界）

前 12 课仍是数据分析入门，**不讲** pandas / Web / 正则体系。第 13 课起另开 Agent 实训，需要 `pydantic`，不要求 GPU。详细知识点见 [`教学内容大纲-Agent.md`](教学内容大纲-Agent.md)。
"""
        outline.write_text(ot, encoding="utf-8")


def write_agent_outline():
    (ROOT / "教学内容大纲-Agent.md").write_text(
        """# Agent 实训 · 教学内容大纲（第13–20课）

| 项目 | 内容 |
|------|------|
| 课程名称 | 私有化模型与 LangGraph / OpenClaw Agent 实训 |
| 适用 | 已完成第 1–12 课 Python 实践，或同等基础 |
| 课次 / 学时 | 8 次课，每次 3 学时，合计约 24 学时 |
| 材料目录 | `第13课-*` … `第20课-*`，共用 `agent_lab/` |
| 配套课表 | [`后续Agent课程安排.md`](后续Agent课程安排.md) |
| 任务分 | 任务一 25 分 + 任务二 35 分 + 任务三 40 分 |

本大纲只回答：**每节课要教哪些知识点、练到什么程度、什么不讲。** 课堂时间盒见各课 `教案.md`。

---

## 1. 课程目标

学生学完第 13–20 课后，应能：

1. 把开源模型收成 OpenAI 兼容 `/v1` 服务，并用 Pydantic 探活与约束 JSON。
2. 把 Agent 写成状态图：Node、Edge、条件边、reducer、Checkpointer、recursion_limit。
3. 初始化 OpenClaw 运行时，完成握手与首轮状态迁移日志。
4. 用 Pydantic 做三级结构化抽取；开发带隔离的 Tool；发现 MCP 元数据；组合 Skill 并自愈。
5. 搭建 RAG 流水线，混合检索与结构化溯源，越界时返回 FallbackResponse。

**不讲**：CUDA 编译、模型微调、商业 Rerank API、多 Agent 辩论平台、pandas。

**环境承诺**：无 GPU 也可 `python3 experiment.py` 通过（Fake `/v1`）。有 Ollama / vLLM 时只改环境变量。

---

## 2. 知识点总表

| 课 | 主题 | 当堂必须讲清的知识点 | 任务分 |
|----|------|----------------------|--------|
| 13 | Serving | `/v1`、探活、JSON 约束、超时 | 前置 |
| 14 | StateGraph | State / reducer / 条件边 / 熔断 / Checkpointer | 前置 |
| 15 | OpenClaw 1.1 | Config 映射、握手、state_log | 10 |
| 16 | 结构化 Prompt | 扁平 / 嵌套 / field_validator | 15 |
| 17 | Tool + MCP | Args/Result、隔离、handshake 清单 | 10+5 |
| 18 | Skill | 单工具、双工具、Self-Correction | 20 |
| 19 | RAG 流水线 | Chunk / 入库 / Retriever Tool | 15 |
| 20 | RAG 调优 | 混合检索、溯源、Fallback | 25 |

---

## 3. 分课知识点

### 第 13 课　模型私有化部署与 Serving

**材料**：`第13课-模型私有化部署与Serving/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | OpenAI 兼容 `/v1/models` 与 `/v1/chat/completions`；Base URL / Key / timeout；Pydantic `HealthReport`；`response_format=json_object` |
| 能力要求 | `probe()` 通过；能解释 Fake 与真实 Ollama/vLLM 只差环境变量 |
| 当堂不讲 | 量化训练、多卡、K8s |
| 前置 | 第 1–12 课 |

### 第 14 课　LangGraph 状态图与 Agent 骨架

**材料**：`第14课-LangGraph状态图与Agent骨架/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | channels 与 reducer；Node 返回增量；条件边 mapping；MemorySaver；recursion_limit |
| 能力要求 | 库存查询走 tool；打招呼不走 tool；自环能熔断 |
| 当堂不讲 | LangGraph Cloud、子图产品化 |
| 前置 | 第 13 课 |

### 第 15 课　OpenClaw 运行时初始化（任务一 1.1）

**材料**：`第15课-OpenClaw运行时初始化/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | OpenClawConfig 映射 LangGraph 状态；handshake=probe；StateTransition 日志 |
| 能力要求 | Client 初始化、探活、打印首轮 state_log |
| 当堂不讲 | 商业控制台 |
| 前置 | 第 13–14 课 |
| 评分 | 10 分 |

### 第 16 课　Pydantic 结构化 Prompt（任务一 1.2）

**材料**：`第16课-Pydantic结构化Prompt/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | JSON Schema 注入 Prompt；UserProfile；TicketAnalysis；DirtyAmount + 对抗拦截 |
| 能力要求 | 三级梯度各有一正；高难另有一反 |
| 当堂不讲 | Pydantic v1 |
| 评分 | 5+5+5=15 分 |

### 第 17 课　自定义 Tool 与 MCP（任务二 2.1+2.2）

**材料**：`第17课-自定义Tool与MCP接入/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | ArgsSchema/ResultSchema；Function Calling 导出；异常隔离；MCP stdio 握手与元数据 |
| 能力要求 | 短 sku 与未知 sku 不崩溃；列出 tools/resources |
| 当堂不讲 | 外部 npx 进程运维 |
| 评分 | 10+5=15 分 |

### 第 18 课　Skill 封装与链式联动（任务二 2.3）

**材料**：`第18课-Skill封装与链式联动/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | Skill 组合 Tool；串行清洗；Self-Correction |
| 能力要求 | 命中 X；MINI 总价 1398；“小部件X”两轮自愈 |
| 当堂不讲 | 多 Agent 辩论 |
| 评分 | 6+7+7=20 分 |

### 第 19 课　RAG 检索流水线（任务三 3.1）

**材料**：`第19课-RAG检索流水线/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | Chunking；教学向量检索；Retriever 封装为 Tool |
| 能力要求 | 续航探针命中手册；Tool 调用成功 |
| 当堂不讲 | Faiss GPU 集群 |
| 评分 | 15 分 |

### 第 20 课　RAG 调优与结构化溯源（任务三 3.2）

**材料**：`第20课-RAG调优与结构化溯源/`

| 类别 | 内容 |
|------|------|
| 核心知识点 | BM25+向量；截断重排；SourcedAnswer；FallbackResponse |
| 能力要求 | 单文档带出处；跨文档对比；天气越界兜底 |
| 当堂不讲 | 微调生成模型 |
| 评分 | 7+9+9=25 分 |

---

## 4. 依赖关系

```text
第13课 Serving
  → 第14课 StateGraph
    → 第15课 OpenClaw 握手（10分）
      → 第16课 Schema 梯度（15分）
        → 第17课 Tool + MCP（15分）
          → 第18课 Skill 链式（20分）
            → 第19课 RAG 流水线（15分）
              → 第20课 溯源与兜底（25分）
```

第 19 课主要依赖第 17 课的 Tool 封装，不依赖 Skill 自愈细节。
""",
        encoding="utf-8",
    )
    (ROOT / "后续Agent课程安排.md").write_text(
        """# Agent 实训 · 8 节课课程安排（第13–20课）

| 项目 | 内容 |
|------|------|
| 课程 | 私有化模型与 Agent 实训 |
| 课次 | **第 13–20 课**，接在 12 节数据分析课之后，不替换前 12 课 |
| 每次课时 | **3 学时连堂** |
| 默认环境 | Jupyter；`pydantic`；无 GPU 使用 `agent_lab` Fake `/v1` |
| 整理日期 | 2026-09-16 |

本文是 **Agent 模块课表**。Python 数据分析 12 课仍以 [`12节课课程安排.md`](12节课课程安排.md) 为准。

---

## 1. 这门模块在干什么

把开源模型变成可探活的 `/v1` 服务，再把 Agent 写成状态图，用 OpenClaw 落地，用 Pydantic 约束一切输入输出，最后用 RAG 给回答加出处、给越界加兜底。

```text
阶段零 Serving → 阶段一 StateGraph → 阶段二 OpenClaw+Schema
       → 阶段三 Tool/MCP/Skill → 阶段四 RAG 溯源
```

**本模块承诺**：无 GPU 学生也能交齐验收脚本；有 GPU 学生只改环境变量对接 Ollama/vLLM。

**本模块不讲**：训练/微调、K8s、商业 Agent 平台后台。

---

## 2. 课次对照

| 本课表 | 文件夹 | 阶段 | 分数 |
|--------|--------|------|------|
| 第 13 课 | `第13课-模型私有化部署与Serving/` | 零 | 前置 |
| 第 14 课 | `第14课-LangGraph状态图与Agent骨架/` | 一 | 前置 |
| 第 15 课 | `第15课-OpenClaw运行时初始化/` | 二 1.1 | 10 |
| 第 16 课 | `第16课-Pydantic结构化Prompt/` | 二 1.2 | 15 |
| 第 17 课 | `第17课-自定义Tool与MCP接入/` | 三 2.1+2.2 | 15 |
| 第 18 课 | `第18课-Skill封装与链式联动/` | 三 2.3 | 20 |
| 第 19 课 | `第19课-RAG检索流水线/` | 四 3.1 | 15 |
| 第 20 课 | `第20课-RAG调优与结构化溯源/` | 四 3.2 | 25 |

学期 Agent 任务分合计 100 分（25+35+40）。前置两课必须通过，否则后续分数不可信。

---

## 3. 时间盒原则

各课 `教案.md` 按 90 分钟书写（与前 12 课同一体例）。3 学时连堂时，余量用于综合练习 P1 与 `experiment.py`。

---

## 4. 验收

```bash
python3 运行全部实验.py
```

Agent 课通过标准仍是脚本打印 `本课验收通过`。讲义综合练习与课后 P1/P2 不得靠复制验收脚本交差。
""",
        encoding="utf-8",
    )


def main():
    for m in META:
        (ROOT / m["folder"]).mkdir(parents=True, exist_ok=True)
        write_docs(m)
    write_plans()
    copy_kb()
    build_lectures()
    build_lectures_rest()
    write_agent_outline()
    update_indexes()
    print("generated 13-20 docs and notebooks")


if __name__ == "__main__":
    main()
