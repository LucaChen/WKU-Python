---
title: Agent 教学大纲
outline: deep
---

# Agent 实训 · 教学内容大纲（第13–20课）

| 项目 | 内容 |
|------|------|
| 课程名称 | 私有化模型与 LangGraph / OpenClaw Agent 实训 |
| 适用 | 已完成第 1–12 课 Python 实践，或同等基础 |
| 课次 / 学时 | 8 次课，每次 3 学时，合计约 24 学时 |
| 材料目录 | `第13课-*` … `第20课-*`，共用 `agent_lab/` |
| 配套课表 | [`后续Agent课程安排.md`](/guide/agent-schedule) |
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
