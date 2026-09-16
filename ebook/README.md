# 课程电子书（VitePress）

在线阅读讲义，并下载 Jupyter 学习。

```bash
cd ebook
npm install
npm run dev
```

浏览器打开终端提示的本地地址（默认 http://localhost:5173/）。

- 页面由 `../_tools/sync_ebook.py` 从各 `第XX课-*` 文件夹生成
- `npm run build` 产出静态站点到 `docs/.vitepress/dist`
- 课程实验目录不要挪走，否则 `experiment.py` 会找不到数据
