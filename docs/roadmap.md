# AI Opportunity Radar — Roadmap

## V1 — 本地日报生成 (已完成)

- [x] GitHub 项目监控（Search API，按 stars 排序）
- [x] arXiv 论文监控（API + feedparser 解析）
- [x] RSS 新闻监控（Hacker News、Hugging Face Papers）
- [x] 规则打分（relevance / actionability / trend / portfolio / novelty）
- [x] 可选 LLM 摘要（OpenAI-compatible，无 key 时规则兜底）
- [x] Markdown 日报输出（`reports/daily/YYYY-MM-DD.md`）
- [x] 容错设计（单源失败不崩溃，打印 WARNING 继续）

## V1.1 — README、示例报告、安全配置 (进行中)

- [x] `.gitignore` 防止误提交 `.env` 和生成数据
- [x] `reports/examples/sample_daily_report.md` 示例日报
- [x] `docs/roadmap.md` 路线图文档
- [x] README 面向作品集优化

## V1.2 — GitHub Actions 每日自动运行

- [ ] `.github/workflows/daily_report.yml` — 每日 UTC 0 点自动运行
- [ ] 支持将日报自动 commit 到仓库或发送到指定位置
- [ ] 可选：GitHub Pages 展示最新日报

## V2 — 接入 Hermes 推送

- [ ] Hermes 微信消息推送集成
- [ ] 可配置推送策略（仅推送 KEEP 级别 / 全部推送）
- [ ] 推送模板自定义

## V3 — 更多数据源

- [ ] 小红书 AI 话题热帖
- [ ] X (Twitter) AI 领域 KOL 动态
- [ ] Reddit r/MachineLearning / r/LocalLLaMA
- [ ] Product Hunt AI 产品榜单
- [ ] 中文技术社区（知乎、掘金）

## V4 — 个人网站展示与作品集包装

- [ ] 日报 Web 前端展示（Next.js / Astro）
- [ ] 历史日报搜索与归档
- [ ] 数据可视化仪表盘（趋势曲线、关键词云）
- [ ] 作品集页面（项目背景、架构、技术栈）
- [ ] 个人网站集成
