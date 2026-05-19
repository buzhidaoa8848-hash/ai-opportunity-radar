# AI Opportunity Radar

> An AI trend & opportunity monitoring system for students and indie builders.
> 面向学生和独立开发者的 AI 趋势与机会监控系统。

---

## 项目定位

每天，GitHub 上有成百上千个新 AI 项目诞生，arXiv 上发布数百篇新论文，Hacker News 和 Hugging Face 上讨论着最新的技术突破。对于学生和独立开发者来说，这些信息散落在不同平台，手动追踪效率极低。

**AI Opportunity Radar** 用一套脚本自动完成数据采集、规则评分和日报生成，让你每天早上打开一份 Markdown 文件，就知道今天该关注什么、该复刻什么、该读什么论文。

### 解决的问题

| 痛点 | 解决方案 |
|------|----------|
| 信息过载 — 每天上千条 AI 动态，看不过来 | 规则打分 + 三级筛选（KEEP/WATCH/IGNORE），只看最相关的 |
| 实习焦虑 — 不知道哪里找 AI 实习/创业机会 | 关键词覆盖实习、初创、比赛，每天自动抓取 |
| 机会分散 — GitHub / arXiv / 新闻分散在不同平台 | 一站式聚合，统一评分和摘要 |
| 选择困难 — 看到好项目不知道要不要跟进 | 每条附带「关注理由」「和我的关系」「建议行动」 |

---

## 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    AI Opportunity Radar                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ collect_     │  │ collect_     │  │ collect_     │   │
│  │ github.py    │  │ arxiv.py     │  │ rss.py       │   │
│  │              │  │              │  │              │   │
│  │ GitHub API   │  │ arXiv API    │  │ RSS/Atom     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         └─────────┬───────┴─────────┬───────┘            │
│                   │                 │                    │
│                   ▼                 ▼                    │
│         ┌─────────────────────────────────┐              │
│         │     score_items.py              │              │
│         │  去重 → 5维评分 → 三级分类      │              │
│         │  relevance / actionability      │              │
│         │  trend / portfolio / novelty    │              │
│         └─────────────┬───────────────────┘              │
│                       │                                  │
│                       ▼                                  │
│         ┌─────────────────────────────────┐              │
│         │   summarize_llm.py (optional)   │              │
│         │  LLM 摘要 或 规则模板兜底       │              │
│         └─────────────┬───────────────────┘              │
│                       │                                  │
│                       ▼                                  │
│         ┌─────────────────────────────────┐              │
│         │   generate_report.py            │              │
│         │  Markdown 日报 + JSON 数据      │              │
│         └─────────────────────────────────┘              │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  config/                  data/       reports/      │  │
│  │  keywords.yaml            raw/        daily/        │  │
│  │  sources.yaml             processed/  examples/     │  │
│  │  scoring.yaml                                      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## V1 功能

- **GitHub 项目监控** — 按关键词搜索仓库，按 stars 降序排列，支持多查询
- **arXiv 论文监控** — 按关键词搜索最新论文，自动解析作者和摘要
- **RSS 新闻监控** — 订阅 Hacker News、Hugging Face Papers 等 RSS 源
- **5 维规则打分** — relevance / actionability / trend / portfolio / novelty，满分 10 分
- **三级筛选** — KEEP (≥8) / WATCH (≥5) / IGNORE (<5)
- **可选 LLM 摘要** — 接入 OpenAI-compatible API，无 API key 时规则模板自动兜底
- **Markdown 日报** — 结构化输出，含 Top 5 机会 + 分类列表 + 3 条行动建议
- **JSON 数据保存** — 原始数据和评分后数据均保存，方便后续分析
- **容错设计** — 任一数据源失败不崩溃，打印 WARNING 继续执行

---

## 示例输出

最新日报示例：[reports/examples/sample_daily_report.md](reports/examples/sample_daily_report.md)

日报包含：
- **今日最高价值机会** — 评分最高的 5 条，每条包含关注理由、和我的关系、建议行动
- **GitHub 项目 Top 10** — 表格概览 + 前 5 条详细分析
- **arXiv 论文 Top 10** — 表格概览 + 前 5 条详细分析（含作者列表）
- **RSS 新闻 Top 10** — 表格概览 + 前 5 条详细分析
- **今日行动建议** — 3 条具体可执行的动作

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| HTTP 请求 | `requests` |
| RSS/Atom 解析 | `feedparser` |
| 配置文件 | `PyYAML` |
| 环境变量 | `python-dotenv` |
| LLM 摘要（可选） | OpenAI-compatible API |

---

## 快速开始

### 1. 安装

```powershell
# 克隆项目
git clone <your-repo-url>
cd ai-opportunity-radar

# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```powershell
copy .env.example .env
```

编辑 `.env`，可选填入：

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx    # 可选，提高 API 限额
LLM_API_KEY=sk-xxxxxxxxxxxx      # 可选，启用 AI 摘要
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

> **不需要任何 API key 也能运行** — 程序会对未认证请求做容错处理，LLM 摘要不可用时自动使用规则模板。

### 3. 运行

```powershell
python scripts/generate_report.py
```

输出：
- `reports/daily/YYYY-MM-DD.md` — Markdown 日报
- `data/processed/YYYY-MM-DD_items.json` — 评分后数据
- `data/raw/YYYY-MM-DD_raw.json` — 原始采集数据

---

## 自定义配置

所有配置在 `config/` 目录，无需修改代码：

| 文件 | 用途 |
|------|------|
| `config/keywords.yaml` | 5 个分类的关键词库，按类别管理 |
| `config/sources.yaml` | 数据源开关、搜索查询、RSS 订阅列表 |
| `config/scoring.yaml` | 5 维评分权重、boost 关键词、KEEP/WATCH 阈值 |

---

## 安全说明

- **`.env` 包含 API key，已加入 `.gitignore`，不会被提交**
- `.env.example` 是配置模板，可以安全提交
- 运行前确认 `GITHUB_TOKEN` 和 `LLM_API_KEY` 未硬编码在任何 `.py` 文件中
- `data/raw/` 和 `data/processed/` 包含每日采集数据，已加入 `.gitignore`
- `reports/daily/` 包含每日生成的日报，已加入 `.gitignore`（示例在 `reports/examples/`）

---

## 项目结构

```
ai-opportunity-radar/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── config/
│   ├── keywords.yaml
│   ├── sources.yaml
│   └── scoring.yaml
├── scripts/
│   ├── collect_github.py
│   ├── collect_arxiv.py
│   ├── collect_rss.py
│   ├── score_items.py
│   ├── summarize_llm.py
│   └── generate_report.py
├── data/
│   ├── raw/               ← gitignored
│   └── processed/         ← gitignored
├── reports/
│   ├── daily/             ← gitignored
│   └── examples/          ← committed
├── docs/
│   └── roadmap.md
└── prompts/
    ├── scoring_prompt.md
    └── daily_report_prompt.md
```

---

## Windows 注意事项

1. **网络**：国内访问 GitHub API / arXiv API 可能需要 VPN。程序遇到网络错误只打印 WARNING，不会崩溃
2. **编码**：如果 PowerShell 中文乱码，先执行 `chcp 65001`
3. **镜像安装**：如果 `pip install` SSL 报错：
   ```powershell
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

---

## 路线图

详见 [docs/roadmap.md](docs/roadmap.md)

| 版本 | 目标 |
|------|------|
| V1 | 本地日报生成 ✅ |
| V1.1 | README、示例报告、安全配置 ✅ |
| V1.2 | GitHub Actions 每日自动运行 |
| V2 | 接入 Hermes 微信推送 |
| V3 | 小红书 / X / Reddit 等更多数据源 |
| V4 | 个人网站展示与作品集包装 |

---

## License

MIT
