# 课程电子书（VitePress）

在线阅读讲义，并下载 Jupyter 学习。

## 本地预览

```bash
cd ebook
npm install
npm run dev
```

浏览器打开终端提示的地址（默认 http://localhost:5173/）。

## 发布到 GitHub Pages（github.io）

推送到 `main` 后，GitHub Actions 会自动构建并部署。

线上地址：

**https://lucachen.github.io/WKU-Python/**

第一次需要在仓库打开 Pages：

1. 打开 https://github.com/LucaChen/WKU-Python/settings/pages
2. **Build and deployment → Source** 选 **GitHub Actions**
3. 打开 https://github.com/LucaChen/WKU-Python/actions 等 **Deploy GitHub Pages** 变绿

本地模拟线上子路径：

```bash
cd ebook
EBOOK_BASE=/WKU-Python/ npm run build
EBOOK_BASE=/WKU-Python/ npm run preview
```

然后访问 http://localhost:4173/WKU-Python/

- 页面由 `../_tools/sync_ebook.py` 从各 `第XX课-*` 文件夹生成
- `npm run build` 产出静态站点到 `docs/.vitepress/dist`
- 课程实验目录不要挪走，否则 `experiment.py` 会找不到数据
