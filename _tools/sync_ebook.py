# -*- coding: utf-8 -*-
"""把课程文件夹同步为 VitePress 电子书页面与可下载 Jupyter 包。"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EBOOK = ROOT / "ebook"
DOCS = EBOOK / "docs"
PUBLIC = DOCS / "public" / "files"
LESSON_OUT = DOCS / "lessons"
GUIDE_OUT = DOCS / "guide"

LESSONS = [
    ("01", "01-environment", "第01课-环境与第一次计算", "环境与第一次计算", "python"),
    ("02", "02-variables", "第02课-变量类型与字符串", "变量类型与字符串", "python"),
    ("03", "03-lists-files-loops", "第03课-列表文件与循环", "列表、文件与循环", "python"),
    ("04", "04-conditions", "第04课-条件判断与筛选", "条件判断与筛选", "python"),
    ("05", "05-dict-freq", "第05课-字典与频数", "字典与频数", "python"),
    ("06", "06-functions-intro", "第06课-函数入门", "函数入门", "python"),
    ("07", "07-functions-advanced", "第07课-函数进阶", "函数进阶", "python"),
    ("08", "08-market-analysis", "第08课-游戏市场综合分析", "游戏市场综合分析", "python"),
    ("09", "09-steam-clean", "第09课-Steam字符串清洗", "Steam 字符串清洗", "python"),
    ("10", "10-year-slice", "第10课-年份切片与摘要", "年份切片与摘要", "python"),
    ("11", "11-snake", "第11课-贪吃蛇与面向对象", "贪吃蛇与面向对象", "python"),
    ("12", "12-datetime", "第12课-模块与日期时间", "模块与日期时间", "python"),
    ("13", "13-serving", "第13课-模型私有化部署与Serving", "模型私有化部署与 Serving", "agent"),
    ("14", "14-langgraph", "第14课-LangGraph状态图与Agent骨架", "LangGraph 状态图与 Agent 骨架", "agent"),
    ("15", "15-openclaw", "第15课-OpenClaw运行时初始化", "OpenClaw 运行时初始化", "agent"),
    ("16", "16-pydantic-prompt", "第16课-Pydantic结构化Prompt", "Pydantic 结构化 Prompt", "agent"),
    ("17", "17-tool-mcp", "第17课-自定义Tool与MCP接入", "自定义 Tool 与 MCP 接入", "agent"),
    ("18", "18-skill-chain", "第18课-Skill封装与链式联动", "Skill 封装与链式联动", "agent"),
    ("19", "19-rag-pipeline", "第19课-RAG检索流水线", "RAG 检索流水线", "agent"),
    ("20", "20-rag-tune", "第20课-RAG调优与结构化溯源", "RAG 调优与结构化溯源", "agent"),
]


def cell_text(cell: dict) -> str:
    src = cell.get("source") or ""
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def escape_vue(text: str) -> str:
    return text.replace("{{", "{<!-- -->{").replace("}}", "}<!-- -->}")


def fence_safe(code: str, lang: str) -> str:
    ticks = "```"
    while ticks in code:
        ticks += "`"
    code = code.rstrip() + "\n"
    return "%s%s\n%s%s\n" % (ticks, lang, code, ticks)


def output_text(cell: dict) -> str:
    chunks = []
    for item in cell.get("outputs") or []:
        if item.get("output_type") == "stream":
            text = item.get("text") or ""
            if isinstance(text, list):
                text = "".join(text)
            chunks.append(text)
        elif item.get("output_type") in ("execute_result", "display_data"):
            data = item.get("data") or {}
            text = data.get("text/plain") or ""
            if isinstance(text, list):
                text = "".join(text)
            if text:
                chunks.append(text)
        elif item.get("output_type") == "error":
            tb = item.get("traceback") or []
            plain = re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(tb))
            chunks.append(plain)
    return "\n".join(chunks).rstrip()


def ipynb_to_md(path: Path, folder: Path, dest: Path, file_base: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for cell in data.get("cells") or []:
        kind = cell.get("cell_type")
        text = cell_text(cell).rstrip()
        if kind == "markdown":
            if text:
                parts.append(rewrite_local_links(text, folder, dest, file_base))
        elif kind == "code":
            parts.append(fence_safe(text if text else "# （此格留给课堂/课后作答）", "python"))
            out = output_text(cell)
            if out:
                parts.append("::: details 运行输出\n\n" + fence_safe(out, "") + "\n:::")
    body = "\n\n".join(parts).strip() + "\n"
    return escape_vue(body)


def rewrite_local_links(text: str, folder: Path, dest: Path, file_base: str) -> str:
    def repl(match: re.Match) -> str:
        bang, label, href = match.group(1), match.group(2), match.group(3)
        if href.startswith(("http://", "https://", "/", "#", "mailto:")):
            return match.group(0)
        target = href.split("#", 1)[0]
        local = folder / target
        if not local.exists():
            found = list(folder.rglob(Path(target).name))
            local = found[0] if found else None
        is_file_link = target.lower().endswith(
            (".ipynb", ".csv", ".py", ".md", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".txt", ".example")
        )
        if local is not None and local.is_file():
            shutil.copy2(local, dest / local.name)
            url = "%s/%s" % (file_base, local.name)
            if bang:
                return "![%s](%s)" % (label, url)
            return "[%s](%s)" % (label, url)
        if bang:
            return "\n\n> 配图 `%s` 未随电子书分发，请下载本课 Jupyter 在原文件夹查看。\n" % target
        if is_file_link:
            return "[%s](%s/%s)" % (label, file_base, Path(target).name)
        return match.group(0)

    return re.sub(r"(!?)\[([^\]]*)\]\(([^)]+)\)", repl, text)


def strip_yaml(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip()
    return text


def read_md(folder: Path, name: str) -> str:
    path = folder / name
    if not path.exists():
        return ""
    return strip_yaml(path.read_text(encoding="utf-8"))


def classify_notebooks(folder: Path):
    lectures = sorted(folder.glob("*学生讲义.ipynb"))
    homework = sorted(folder.glob("*课后练习.ipynb"))
    extras = []
    if not lectures:
        for path in sorted(folder.glob("experiment*.ipynb")):
            if path.name == "experiment.ipynb":
                extras.append(path)
            else:
                lectures.append(path)
    else:
        accept = folder / "experiment.ipynb"
        if accept.exists():
            extras.append(accept)
    return lectures, homework, extras


def copy_assets(folder: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    patterns = [
        "*.ipynb",
        "*.csv",
        "*.py",
        "*.svg",
        "*.png",
        "*.md",
        "*.example",
        "kb/*.md",
        "images/*",
    ]
    skip_names = {"README.md", "教案.md", "实验说明.md"}
    for pattern in patterns:
        for path in folder.glob(pattern):
            if not path.is_file():
                continue
            if path.name in skip_names:
                continue
            if path.suffix == ".ipynb" and ".ipynb_checkpoints" in str(path):
                continue
            target = dest / path.name
            shutil.copy2(path, target)


def zip_lesson(folder: Path, dest_zip: Path, include_agent: bool) -> None:
    if dest_zip.exists():
        dest_zip.unlink()
    skip = {".ipynb_checkpoints", "__pycache__"}
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            if any(part in skip for part in path.parts):
                continue
            if path.name in {".DS_Store"}:
                continue
            rel = path.relative_to(folder)
            zf.write(path, "%s/%s" % (folder.name, rel.as_posix()))
        if include_agent:
            lab = ROOT / "agent_lab"
            for path in lab.rglob("*"):
                if not path.is_file():
                    continue
                if any(part in skip for part in path.parts):
                    continue
                rel = path.relative_to(ROOT)
                zf.write(path, rel.as_posix())


def download_buttons(slug: str, lectures, homework, extras) -> str:
    lines = ['<div class="dl-row">']
    for path in lectures:
        lines.append(
            '<a class="dl-btn" href="/files/%s/%s" download>下载讲义 · %s</a>'
            % (slug, path.name, path.name)
        )
    for path in homework:
        lines.append(
            '<a class="dl-btn brand" href="/files/%s/%s" download>下载课后练习 · %s</a>'
            % (slug, path.name, path.name)
        )
    lines.append(
        '<a class="dl-btn ghost" href="/files/%s/lesson.zip" download>下载本课材料包 zip</a>' % slug
    )
    lines.append("</div>")
    if extras:
        extra = "、".join("`%s`" % p.name for p in extras)
        lines.append("\n验收笔记本（已填好，可对照）：%s\n" % extra)
    return "\n".join(lines)


def write_lesson_page(num, slug, folder_name, title, part) -> dict:
    folder = ROOT / folder_name
    dest = PUBLIC / slug
    if dest.exists():
        shutil.rmtree(dest)
    copy_assets(folder, dest)
    include_agent = part == "agent"
    zip_lesson(folder, dest / "lesson.zip", include_agent=include_agent)

    lectures, homework, extras = classify_notebooks(folder)
    readme = read_md(folder, "README.md")
    intro = read_md(folder, "实验说明.md")
    plan = read_md(folder, "教案.md")

    chunks = [
        "---",
        "title: 第%s课 %s" % (num, title),
        "outline: deep",
        "---",
        "",
        "# 第%s课　%s" % (num, title),
        "",
        '<p class="lesson-kicker">%s · 文件夹 <code>%s</code></p>'
        % ("Python 数据分析" if part == "python" else "Agent 实训", folder_name),
        "",
        download_buttons(slug, lectures, homework, extras),
        "",
        "## 本课说明",
        "",
        readme.strip() or "见课程文件夹 README。",
        "",
    ]
    if intro.strip():
        chunks += ["## 实验说明", "", intro.strip(), ""]

    for path in lectures:
        heading = "课堂讲义"
        if len(lectures) > 1:
            heading = "课堂讲义 · %s" % path.stem
        chunks += [
            "## %s" % heading,
            "",
            "> 以下由 Jupyter 转换，便于在线阅读。请下载 `.ipynb` 在本地内核中练习。",
            "",
            ipynb_to_md(path, folder, dest, "/files/%s" % slug),
            "",
        ]
    for path in homework:
        chunks += [
            "## 课后练习 · %s" % path.stem,
            "",
            "> 练习格在电子书中为空，下载 Jupyter 后作答。",
            "",
            ipynb_to_md(path, folder, dest, "/files/%s" % slug),
            "",
        ]
    if plan.strip():
        chunks += ["## 教案（教师）", "", plan.strip(), ""]

    LESSON_OUT.mkdir(parents=True, exist_ok=True)
    (LESSON_OUT / ("%s.md" % slug)).write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return {
        "num": num,
        "slug": slug,
        "title": title,
        "part": part,
        "folder": folder_name,
        "lectures": [p.name for p in lectures],
        "homework": [p.name for p in homework],
    }


def copy_guide(src_name: str, dest_name: str, title: str) -> None:
    src = ROOT / src_name
    text = src.read_text(encoding="utf-8") if src.exists() else "# %s\n\n（源文件缺失）\n" % title
    text = strip_yaml(text)
    text = text.replace("](教学内容大纲.md)", "](/guide/python-outline)")
    text = text.replace("](教学内容大纲-Agent.md)", "](/guide/agent-outline)")
    text = text.replace("](12节课课程安排.md)", "](/guide/python-schedule)")
    text = text.replace("](后续Agent课程安排.md)", "](/guide/agent-schedule)")
    text = text.replace("](README.md)", "](/)")
    body = "---\ntitle: %s\noutline: deep\n---\n\n%s" % (title, text)
    GUIDE_OUT.mkdir(parents=True, exist_ok=True)
    (GUIDE_OUT / dest_name).write_text(body, encoding="utf-8")


def write_downloads(infos) -> None:
    lines = [
        "---",
        "title: 下载中心",
        "---",
        "",
        "# 下载中心",
        "",
        "所有 Jupyter 均可在浏览器打开对应课次后单独下载，也可按课打包。Agent 课的材料包内含 `agent_lab/`，也可单独下载 [agent_lab.zip](/files/agent_lab.zip)。",
        "",
        "## 按课下载",
        "",
        "| 课次 | 讲义 | 课后练习 | 材料包 |",
        "| --- | --- | --- | --- |",
    ]
    for info in infos:
        lec = "<br>".join(
            '[%s](/files/%s/%s)' % (name, info["slug"], name) for name in info["lectures"]
        ) or "—"
        hw = "<br>".join(
            '[%s](/files/%s/%s)' % (name, info["slug"], name) for name in info["homework"]
        ) or "—"
        lines.append(
            "| [第%s课 %s](/lessons/%s) | %s | %s | [lesson.zip](/files/%s/lesson.zip) |"
            % (info["num"], info["title"], info["slug"], lec, hw, info["slug"])
        )
    lines += [
        "",
        "## 使用建议",
        "",
        "1. 下载后与 csv / `kb/` 放在同一文件夹，从该文件夹启动 Jupyter 内核。",
        "2. 第 13–20 课需要能 `import agent_lab`：材料包已带上，或把课程根目录加入 `sys.path`。",
        "3. 第 9–10 课完整 `steam.csv` 约 5.5MB，已打进对应课次 zip；课后练习用 `steam_sample.csv` 即可。",
        "",
    ]
    (DOCS / "downloads.md").write_text("\n".join(lines), encoding="utf-8")


def write_sidebar(infos) -> None:
    python_items = [
        {"text": "教学大纲", "link": "/guide/python-outline"},
        {"text": "课程安排", "link": "/guide/python-schedule"},
    ]
    agent_items = [
        {"text": "教学大纲", "link": "/guide/agent-outline"},
        {"text": "课程安排", "link": "/guide/agent-schedule"},
        {"text": "agent_lab 运行时", "link": "/guide/agent-runtime"},
    ]
    for info in infos:
        item = {"text": "第%s课 %s" % (info["num"], info["title"]), "link": "/lessons/%s" % info["slug"]}
        if info["part"] == "python":
            python_items.append(item)
        else:
            agent_items.append(item)
    sidebar = [
        {
            "text": "开始",
            "items": [
                {"text": "如何阅读与下载", "link": "/guide/start"},
                {"text": "下载中心", "link": "/downloads"},
            ],
        },
        {"text": "Python 数据分析 · 第1–12课", "collapsed": False, "items": python_items},
        {"text": "Agent 实训 · 第13–20课", "collapsed": False, "items": agent_items},
    ]
    (DOCS / ".vitepress" / "sidebar.generated.js").write_text(
        "export const sidebar = %s\n" % json.dumps(sidebar, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_start_page() -> None:
    GUIDE_OUT.mkdir(parents=True, exist_ok=True)
    (GUIDE_OUT / "start.md").write_text(
        """---
title: 如何阅读与下载
---

# 如何阅读与下载

这本电子书把课程文件夹里的 **学生讲义** 和 **课后练习** Jupyter 转成网页，方便预习和检索；真正动手请下载 `.ipynb`。

## 阅读

1. 左侧按课次打开章节。
2. 每课顺序：说明 → 讲义 → 课后练习 → 教师教案。
3. 讲义里的案例代码可以直接在网页上看；标了「留给作答」的格子是空的，需要在 Jupyter 里完成。

## 下载 Jupyter

每课页顶部有按钮：

- **下载讲义**：课堂用笔记本
- **下载课后练习**：P1 / P2 必做，P3 选做
- **材料包 zip**：笔记本 + 本课 csv / 脚本 / 知识库（Agent 课含 `agent_lab`）

也可以去 [下载中心](/downloads) 一次找齐。

## 本地怎么跑

```bash
# 在解压后的课次文件夹里
python3 experiment.py
```

第 11 课游玩：

```bash
python3 snake.py
```

需要：Python 3.9+。第 3–12 课只用标准库；第 13–20 课需要 `pydantic`，**不要求 GPU**。

## 和课程文件夹的关系

电子书只是阅读层。开课材料仍在各 `第XX课-*/` 目录，验收脚本路径没有改。
""",
        encoding="utf-8",
    )


def zip_agent_lab() -> None:
    dest = PUBLIC / "agent_lab.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    lab = ROOT / "agent_lab"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in lab.rglob("*"):
            if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(ROOT).as_posix())


def main() -> None:
    LESSON_OUT.mkdir(parents=True, exist_ok=True)
    GUIDE_OUT.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (DOCS / ".vitepress").mkdir(parents=True, exist_ok=True)

    if PUBLIC.exists():
        for child in PUBLIC.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            elif child.name.endswith(".zip"):
                child.unlink()

    infos = []
    for item in LESSONS:
        print("sync", item[0], item[3])
        infos.append(write_lesson_page(*item))

    copy_guide("教学内容大纲.md", "python-outline.md", "Python 教学大纲")
    copy_guide("12节课课程安排.md", "python-schedule.md", "Python 课程安排")
    copy_guide("教学内容大纲-Agent.md", "agent-outline.md", "Agent 教学大纲")
    copy_guide("后续Agent课程安排.md", "agent-schedule.md", "Agent 课程安排")
    copy_guide("agent_lab/README.md", "agent-runtime.md", "agent_lab 运行时")
    write_start_page()
    write_downloads(infos)
    write_sidebar(infos)
    zip_agent_lab()
    print("ebook synced", len(infos), "lessons")


if __name__ == "__main__":
    main()
