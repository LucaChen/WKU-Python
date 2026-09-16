import { defineConfig } from 'vitepress'
import { sidebar } from './sidebar.generated.js'

const rawBase = process.env.EBOOK_BASE || '/'
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`

export default defineConfig({
  lang: 'zh-CN',
  title: 'WKU Python 实践课',
  description: '数据分析入门与 Agent 实训电子书：在线阅读讲义，下载 Jupyter 动手做。',
  base,
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,
  markdown: {
    lineNumbers: true,
  },
  head: [
    ['link', { rel: 'icon', href: `${base}favicon.svg` }],
  ],
  themeConfig: {
    logo: '/favicon.svg',
    outline: { level: [2, 3], label: '本页目录' },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除',
            backButtonTitle: '关闭',
            noResultsText: '没有结果',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' },
          },
        },
      },
    },
    nav: [
      { text: '开始', link: '/guide/start' },
      { text: '第1–12课', link: '/lessons/01-environment' },
      { text: '第13–20课', link: '/lessons/13-serving' },
      { text: '下载 Jupyter', link: '/downloads' },
    ],
    sidebar,
    docFooter: { prev: '上一课', next: '下一课' },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色',
    darkModeSwitchTitle: '切换到深色',
  },
})
