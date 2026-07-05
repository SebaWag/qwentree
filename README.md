# 🌳 QwenTree — Multimodal Tree File Agent

**QwenTree** is a **Tree File Agent** built on **Qwen Cloud**'s multimodal models. It organizes its capabilities as a navigable file system, where each *skill* is a file the agent can list, read, and execute.

> 🏆 **Global AI Hackathon Series with Qwen Cloud 2026** — Track: Agent Society

---

## 🧠 Architecture

```
qwentree> what do you see in this image?
     │
     ▼
┌─────────────────────────────────────────────┐
│  🧠 ORCHESTRATOR (Qwen3.7-Max)              │
│  Analyzes → Routes → Invokes skills         │
├──────────────────┬──────────────────────────┤
│                  │                          │
│  🌳 TREE        │  🗄️ MEMORY (3 tiers)      │
│  NAVIGATOR      │                           │
│                  │  🏛️ Mental Models (Chroma)│
│  skills/vision/  │  📝 Observations (PgSQL) │
│  skills/code/   │  📦 Raw Facts (Redis)     │
│  skills/web/    │                           │
│  skills/audio/  │  🧠 LIVING BRAIN          │
│  skills/video/  │  (real sessions ingested) │
│  skills/files/  │                           │
│  ...            │                           │
└──────────────────┴──────────────────────────┘
```

## ✨ Key Differentiators

| Feature | How QwenTree does it |
|---------|---------------------|
| 🏛️ **Tree-File Architecture** | Skills as navigable files — the agent `ls`, `cd`, `cat` over its own capabilities |
| 👁️ **True Multimodal** | Not just text — image, audio, video, code, web — **fully integrated** |
| 🧠 **Living Memory** | 3-tier memory (ChromaDB + PostgreSQL + Redis) populated with **6,099 items** from 212 real development sessions |
| 🔧 **Extensible like SHIVA** | Add a skill = create a `.py` file in the right folder |
| 💻 **CLI-first with Textual TUI** | Native terminal with rich formatting, panels, autocomplete |
| 🔗 **Ecosystem Integration** | Connects with n8n, SHIVA, Academy, databases |

## 🧩 Skills — 31 across 10 categories

```
qwentree/skills/
├── vision/     👁️  Analyze images, OCR, URL analysis (Qwen-VL)
├── audio/      🎤  Transcribe speech, synthesize voice (Qwen-Audio, CosyVoice)
├── video/      🎬  Analyze videos, extract frames (Qwen-VL + FFmpeg)
├── code/       💻  Execute Python, analyze code, refactor
├── web/        🌐  Search web, fetch pages (Playwright)
├── files/      📁  Read, write, search, tree, find by content
├── system/     ⚙️  System info, shell commands
├── memory/     🧠  Recall past sessions, search 3-tier memory
├── media/      🎨  Generate images (Wan) & videos (HappyHorse #1)
└── integrations/ 🔗  SHIVA, n8n, Academy
```

## 🧠 Living Brain — Memory Architecture

QwenTree uses a **3-tier hierarchical memory system** inspired by cognitive science:

| Tier | Storage | Content | Size |
|:----:|:-------:|:--------|:----:|
| 🏛️ **Mental Models** | ChromaDB | Canonical facts extracted from sessions | 3,046 items |
| 📝 **Observations** | PostgreSQL | Patterns, decisions, learnings | 2,751 items |
| 📦 **Raw Facts** | Redis | Full session transcripts with metadata | 212 sessions |
| | | **TOTAL** | **6,099 items** |

The memory was **auto-populated from 212 real development sessions**, making the agent functional from day one.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/SebaWag/qwentree.git
cd qwentree

# 2. Environment
cp .env.example .env
# Edit .env with your QwenCloud API key

# 3. Dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 4. Infrastructure (Docker)
docker compose up -d  # Redis + PostgreSQL + ChromaDB

# 5. Populate memory (ingest sessions)
python3 -m scripts.ingest_brain

# 6. Run!
python3 -m qwentree
```

## 🖥️ CLI Usage

```bash
# Launch TUI
python3 -m qwentree

# Commands inside TUI
/help              # Show all commands
/ls                # List all skill categories
/tree              # Show full skill tree
/stats             # Show system statistics
/mode qwen|local   # Switch API mode

# Or use direct CLI mode
python3 -m qwentree --cli
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| 🧠 **LLM Orchestrator** | Qwen3.7-Max / Qwen3.7-Plus |
| 👁️ **Vision** | Qwen-VL-Max |
| 🎤 **Audio** | Qwen-Audio + CosyVoice-01 |
| 🎬 **Video Generation** | HappyHorse-1.1-T2V (#1 worldwide) |
| 🖼️ **Image Generation** | Wan |
| 🧠 **Memory** | ChromaDB + PostgreSQL + Redis |
| 🖥️ **CLI** | Textual (Python TUI framework) |
| 🌐 **Web** | Playwright + httpx + BeautifulSoup |
| 🐳 **Infra** | Docker Compose |

## 📊 Project Stats

```
📁 Files:       48 Python files
📝 Lines:       3,818 lines of code
🧩 Skills:      31 skills in 10 categories
🧠 Memory:      6,099 items (3 tiers)
🧪 Tests:       89 tests (all passing)
```

## 📄 License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for the <strong>Global AI Hackathon Series with Qwen Cloud 2026</strong><br>
  <a href="https://github.com/SebaWag/qwentree">🌳 QwenTree on GitHub</a>
</p>
