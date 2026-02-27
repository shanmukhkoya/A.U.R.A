# 🤖 Autonomous Research & Solution Architect Agent

An **autonomous AI agent** that thinks, plans, researches, reflects, and generates comprehensive reports — all on its own. Built for Contact Center, VoIP, CTI, and enterprise communications research, but works for **any domain**.

```
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   📋 PLAN   │────▶│ 🔍 RESEARCH │────▶│ 🤔 REFLECT  │────▶│  📝 REPORT  │
  │ Break down  │     │ Search web  │     │ Self-evaluate│     │ Synthesize  │
  │ the goal    │     │ Extract data│     │ Find gaps    │     │ final report│
  └─────────────┘     └─────────────┘     └──────┬───────┘     └─────────────┘
                                                 │
                                          Not satisfied?
                                                 │
                                          ┌──────▼───────┐
                                          │ 🔄 ITERATE   │
                                          │ Research more │
                                          └──────────────┘
```

## ✨ Features

- **Truly Autonomous** — Plans, executes, self-evaluates, and iterates without human input
- **Multi-Provider LLM Support** — Works with:
  - 🖥️ **Ollama** (Local, FREE — llama3, mistral, phi3, gemma2)
  - 🟢 **OpenAI** (GPT-4o, GPT-4o-mini)
  - 🟣 **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus)
  - 🔵 **Google** (Gemini 2.0 Flash, Gemini 1.5 Pro)
  - 🔗 Any **OpenAI-compatible API** (Groq, Together, LM Studio)
- **Web Search** — DuckDuckGo + Google News RSS (no API keys needed)
- **Smart Content Extraction** — Extracts relevant text from web pages
- **Self-Reflection Loop** — Evaluates its own work quality and fills gaps
- **Beautiful Web UI** — Real-time visualization of agent's thought process
- **CLI Interface** — Beautiful terminal output with colors
- **Lightweight** — Minimal dependencies, runs on constrained hardware

## 🚀 Quick Start

### 1. Setup

```bash
# Navigate to the project
cd autonomous-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (Optional)

Edit `config.yaml` to set your preferred provider and model.

For cloud providers, copy `.env.example` to `.env` and add your API keys:
```bash
copy .env.example .env
# Then edit .env with your keys
```

### 3. Run — CLI Mode

```bash
# Interactive mode
python run.py

# With a specific goal
python run.py "Design a CCaaS migration plan from Avaya to Genesys Cloud"

# Override provider and model
python run.py --provider openai --model gpt-4o "Compare SIP trunk providers"

# Exhaustive research
python run.py --depth exhaustive "AI-powered contact center architecture"
```

### 4. Run — Web UI Mode

```bash
python web/server.py
# Open http://localhost:5000
```

## 🏗️ Architecture

```
autonomous-agent/
├── agent/                    # Core agent package
│   ├── core.py              # 🧠 Main autonomous loop
│   ├── planner.py           # 📋 Goal → research tasks
│   ├── executor.py          # 🔍 Search → extract → analyze
│   ├── reflector.py         # 🤔 Self-evaluation & iteration
│   ├── memory.py            # 💾 Working memory
│   ├── prompts.py           # 📝 All prompt templates
│   ├── config.py            # ⚙️ Configuration manager
│   └── providers/           # 🤖 LLM providers
│       ├── base.py          # Abstract interface
│       ├── ollama.py        # Local models
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       └── google_provider.py
├── agent/tools/             # 🔧 Agent tools
│   ├── web_search.py        # Web search (DuckDuckGo + RSS)
│   └── content_extractor.py # Web page text extraction
├── web/                     # 🌐 Web UI
│   ├── server.py            # Flask backend + SSE
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config.yaml              # Configuration
├── run.py                   # CLI entry point
└── outputs/                 # Generated reports
```

## ⚙️ Configuration

### Switch Providers

Edit `config.yaml`:
```yaml
# Use local Ollama
provider: ollama
ollama:
  model: llama3

# Use OpenAI
provider: openai
openai:
  model: gpt-4o-mini

# Use Anthropic
provider: anthropic
anthropic:
  model: claude-3-5-sonnet-20241022
```

### Agent Behavior

```yaml
agent:
  max_iterations: 3        # Max reflect-iterate cycles
  max_search_results: 5    # Results per search query
  research_depth: detailed # quick | detailed | exhaustive
```

## 🧠 How It Works

1. **PLAN** — The agent receives your goal and uses the LLM to break it into 3-8 focused research queries
2. **RESEARCH** — For each query, it searches the web, extracts content from top pages, and analyzes findings
3. **REFLECT** — After researching, it evaluates completeness (1-10) and depth (1-10), identifies gaps
4. **ITERATE** — If quality is below threshold, it generates new queries and researches more
5. **SYNTHESIZE** — Once satisfied, it generates a comprehensive markdown report with sections, tables, and recommendations

## 📄 License

MIT License — use freely for any purpose.
