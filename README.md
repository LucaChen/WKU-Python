# Python 实践课 · 按课归档

GitHub：[LucaChen/WKU-Python](https://github.com/LucaChen/WKU-Python)

本目录是开课用的 **12 节 Python 数据分析课**，外加 **8 节 Agent 实训课**（第13–20课）。每一课一个文件夹，内含实验说明、教案、数据、可运行实验。

- 电子书（在线阅读 + 下载 Jupyter）：[`ebook/`](ebook/README.md)，本地 `cd ebook && npm install && npm run dev`
- GitHub Pages：https://lucachen.github.io/WKU-Python/ （需在仓库 Settings → Pages 将 Source 设为 GitHub Actions）
- 每课要教的知识点：[`教学内容大纲.md`](教学内容大纲.md)（第13–20课见 [`教学内容大纲-Agent.md`](教学内容大纲-Agent.md)）
- 学期安排与验收口径：[`12节课课程安排.md`](12节课课程安排.md)（Agent 模块见 [`后续Agent课程安排.md`](后续Agent课程安排.md)）
- 内部生成脚本：[`_tools/`](_tools/README.md)（不要改各课文件夹路径）

| 文件夹 | 当堂主实验 | 数据 |
|--------|------------|------|
| [第01课-环境与第一次计算](第01课-环境与第一次计算) | `experiment.py` / 讲义 `experiment1.ipynb` | 无 |
| [第02课-变量类型与字符串](第02课-变量类型与字符串) | `experiment.py` / 讲义 `experiment2-*.ipynb` | 无 |
| [第03课-列表文件与循环](第03课-列表文件与循环) | 讲义 `chapter03_列表文件与循环_学生讲义.ipynb` / 课后 `chapter03_列表文件与循环_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第04课-条件判断与筛选](第04课-条件判断与筛选) | 讲义 `chapter04_条件与判断_学生讲义.ipynb` / 课后 `chapter04_条件与判断_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第05课-字典与频数](第05课-字典与频数) | 讲义 `chapter05_字典与频数_学生讲义.ipynb` / 课后 `chapter05_字典与频数_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第06课-函数入门](第06课-函数入门) | 讲义 `chapter06_函数入门_学生讲义.ipynb` / 课后 `chapter06_函数入门_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第07课-函数进阶](第07课-函数进阶) | 讲义 `chapter07_函数进阶_学生讲义.ipynb` / 课后 `chapter07_函数进阶_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第08课-游戏市场综合分析](第08课-游戏市场综合分析) | 讲义 `chapter08_游戏市场综合分析_学生讲义.ipynb` / 课后 `chapter08_游戏市场综合分析_课后练习.ipynb` / 验收 `experiment.py` | `mobile_game_info.csv`；课后 `googleplaystore.csv` |
| [第09课-Steam字符串清洗](第09课-Steam字符串清洗) | 讲义 `chapter09_Steam字符串清洗_学生讲义.ipynb` / 课后 `chapter09_Steam字符串清洗_课后练习.ipynb` / 验收 `experiment.py` | `steam.csv`；课后 `steam_sample.csv` |
| [第10课-年份切片与摘要](第10课-年份切片与摘要) | 讲义 `chapter10_年份切片与摘要_学生讲义.ipynb` / 课后 `chapter10_年份切片与摘要_课后练习.ipynb` / 验收 `experiment.py` | `steam.csv`；课后 `steam_sample.csv` |
| [第11课-贪吃蛇与面向对象](第11课-贪吃蛇与面向对象) | 讲义 `chapter11_贪吃蛇与面向对象_学生讲义.ipynb` / 课后 `chapter11_贪吃蛇与面向对象_课后练习.ipynb` / 游玩 `snake.py` / 验收 `experiment.py` | 无 |
| [第12课-模块与日期时间](第12课-模块与日期时间) | 讲义 `chapter12_模块与日期时间_学生讲义.ipynb` / 课后 `chapter12_模块与日期时间_课后练习.ipynb` / 验收 `experiment.py` | `covid_sample.csv` |

## 怎么跑

在对应课的文件夹里：

```bash
python3 experiment.py
```

第 11 课键盘游玩：

```bash
python3 snake.py
```

自动验收（能动、能吃、能撞墙死）：

```bash
python3 snake.py --demo
```

第 1–2 课的 `experiment2-*.ipynb` 是原讲义练习册（格子多为空，留给学生填）。第 3–20 课讲义为 `chapterXX_*_学生讲义.ipynb`，课后作业为 `chapterXX_*_课后练习.ipynb`。`experiment.py` 是已填好的验收版。

## 批量自测

```bash
python3 运行全部实验.py
```

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

## 电子书

```bash
cd ebook
npm install
npm run dev
```

浏览器打开提示的地址。每课页可阅读讲义，并下载 `.ipynb` 或本课 `lesson.zip`。
