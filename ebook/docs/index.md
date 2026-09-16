---
layout: home
hero:
  name: WKU Python 实践课
  text: 数据分析入门，再进入 Agent 实训
  tagline: 在线阅读 20 课讲义与课后练习，一键下载 Jupyter 动手做。无需 GPU 即可完成 Agent 模块验收。
  actions:
    - theme: brand
      text: 开始阅读
      link: /guide/start
    - theme: alt
      text: 下载 Jupyter
      link: /downloads
features:
  - title: 第 1–12 课 · Python 数据分析
    details: 从 Jupyter 第一次计算，到 csv 清洗、字典频数、函数、Steam 摘要、贪吃蛇与日期时间。
    link: /lessons/01-environment
    linkText: 从第 01 课开始
  - title: 第 13–20 课 · Agent 实训
    details: 私有化 Serving、LangGraph 状态图、OpenClaw、Pydantic、Tool/MCP、Skill 链式调用与 RAG 溯源。
    link: /lessons/13-serving
    linkText: 从阶段零开始
  - title: 下载即练
    details: 每课提供讲义 .ipynb、课后练习与材料包 zip（含 csv / 知识库；Agent 课含 agent_lab）。
    link: /downloads
    linkText: 打开下载中心
---

## 怎么用这本电子书

1. 左侧目录按课阅读，网页展示的是 Jupyter 转换后的内容。
2. 需要作答的格子请 **下载 `.ipynb`**，与 csv 放在同一文件夹后启动内核。
3. 验收仍在课程文件夹执行 `python3 experiment.py`，与电子书互不影响。

本地预览电子书：

```bash
cd ebook
npm install
npm run dev
```
