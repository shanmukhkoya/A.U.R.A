# 🤖 Autonomous Research Agent — Complete Technical Documentation

> **Easy language · Technically in-depth · Self-explanatory**
>
> This document explains every single part of the Autonomous Research & Solution Architect Agent — from the big picture down to every function, prompt, and configuration option. Whether you're a developer, a curious learner, or someone who just wants to use this tool, this guide has you covered.

---

## Table of Contents

1. [What Is This Bot?](#1-what-is-this-bot)
2. [Architecture Overview](#2-architecture-overview)
3. [Tech Stack](#3-tech-stack)
4. [How It Works — The Agent Loop](#4-how-it-works--the-agent-loop)
5. [Project Structure](#5-project-structure)
6. [Module-by-Module Deep Dive](#6-module-by-module-deep-dive)
   - [6.1 Core Agent (core.py)](#61-core-agent--corepy)
   - [6.2 Planner (planner.py)](#62-planner--plannerpy)
   - [6.3 Executor (executor.py)](#63-executor--executorpy)
   - [6.4 Reflector (reflector.py)](#64-reflector--reflectorpy)
   - [6.5 Memory (memory.py)](#65-working-memory--memorypy)
   - [6.6 Config (config.py)](#66-configuration--configpy)
   - [6.7 Prompts (prompts.py)](#67-prompt-engineering--promptspy)
7. [LLM Providers](#7-llm-providers)
   - [7.1 Base Provider (base.py)](#71-base-provider--basepy)
   - [7.2 Ollama — Local Models (ollama.py)](#72-ollama--local-models)
   - [7.3 OpenAI (openai_provider.py)](#73-openai)
   - [7.4 Anthropic Claude (anthropic_provider.py)](#74-anthropic-claude)
   - [7.5 Google Gemini (google_provider.py)](#75-google-gemini)
8. [Tools](#8-tools)
   - [8.1 Web Search (web_search.py)](#81-web-search--web_searchpy)
   - [8.2 Content Extractor (content_extractor.py)](#82-content-extractor--content_extractorpy)
9. [Web UI](#9-web-ui)
   - [9.1 Flask Server (server.py)](#91-flask-server--serverpy)
   - [9.2 Frontend (app.js)](#92-frontend--appjs)
   - [9.3 HTML Structure (index.html)](#93-html-structure--indexhtml)
   - [9.4 Styling (style.css)](#94-styling--stylecss)
10. [CLI Interface (run.py)](#10-cli-interface--runpy)
11. [Configuration & Customization](#11-configuration--customization)
12. [Making It Your Own — Customization Guide](#12-making-it-your-own--customization-guide)
13. [API Reference](#13-api-reference)
14. [Performance Optimization — Small Model Mode](#14-performance-optimization--small-model-mode)
15. [Setup & Installation](#15-setup--installation)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. What Is This Bot?

Imagine you have a personal research assistant who can:
1. **Understand** any research question you throw at it
2. **Plan** what to search for (breaking your question into smaller, searchable piece)
3. **Research** the internet — finding articles, extracting text, reading web pages
4. **Think critically** — analyzing what it found, identifying gaps
5. **Self-evaluate** — asking itself "Is this good enough? What am I missing?"
6. **Write a report** — producing a professional, well-structured document with findings and recommendations

That's exactly what this bot does. It's an **autonomous agent** — meaning once you give it a goal, it runs on its own through all these steps without you needing to intervene. It can even decide "I need more research" and loop back to search for more information.

### Key Capabilities
- **Works with any LLM** — runs locally with Ollama (free!) or with cloud APIs (OpenAI, Anthropic, Google)
- **Real-time visualization** — watch the agent think in a beautiful web UI
- **Any topic** — while originally designed for Contact Center/VoIP topics, it can research absolutely anything
- **Auto-saves reports** — every research report is saved as a Markdown file

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER                                      │
│                    (Web UI or CLI)                                │
└─────────────┬───────────────────────────────────┬───────────────┘
              │ Goal: "Research X topic"           │ Real-time logs
              ▼                                    ▲
┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS AGENT (core.py)                    │
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │ PLANNER  │───▶│ EXECUTOR │───▶│REFLECTOR │───▶│SYNTHESIZE│  │
│   │          │    │          │    │          │    │          │  │
│   │ Break    │    │ Search   │    │ Evaluate │    │ Generate │  │
│   │ goal into│    │ the web, │    │ quality, │    │ the final│  │
│   │ tasks    │    │ extract  │    │ identify │    │ Markdown │  │
│   │          │    │ content, │    │ gaps,    │    │ report   │  │
│   │          │    │ analyze  │    │ decide   │    │          │  │
│   └──────────┘    └──────────┘    │ to loop  │    └──────────┘  │
│                         ▲         │ or stop  │                   │
│                         │         └────┬─────┘                   │
│                         │              │                         │
│                         └──────────────┘                         │
│                     (loop if MORE research needed)               │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │                  WORKING MEMORY (memory.py)              │   │
│   │  Stores: goal, plan, findings, reflections, logs         │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│   │ LLM PROVIDER │  │  WEB SEARCH  │  │ CONTENT EXTRACTOR   │  │
│   │ (Ollama/     │  │ (DuckDuckGo) │  │ (BeautifulSoup)     │  │
│   │  OpenAI/     │  │              │  │                     │  │
│   │  Anthropic/  │  │              │  │                     │  │
│   │  Google)     │  │              │  │                     │  │
│   └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### The Flow in Plain English

1. **You** type a research goal (e.g., "What is SIP trunking?")
2. The **Planner** asks the LLM to break this into 3-8 specific search queries
3. The **Executor** runs each query:
   - Searches DuckDuckGo for results
   - Extracts text from the top web pages
   - Asks the LLM to analyze the findings
4. The **Reflector** asks the LLM to evaluate the research quality (1-10 scores)
5. If quality is insufficient, it loops back to step 3 with new queries
6. Once satisfied, the **Synthesizer** asks the LLM to write a comprehensive report
7. The report is saved as a `.md` file and displayed in the UI

---

## 3. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Language** | Python 3.10+ | Easy to read, great AI/ML ecosystem |
| **Web Framework** | Flask | Lightweight, simple, perfect for a single-page app |
| **Real-time Updates** | Server-Sent Events (SSE) | One-way streaming from server to browser — simpler than WebSockets |
| **Frontend** | Vanilla HTML/CSS/JS | No build step, no npm, just open and go |
| **Web Scraping** | BeautifulSoup4 | The gold standard for HTML parsing in Python |
| **Search Engine** | DuckDuckGo (HTML) | No API key needed, free, private |
| **Fallback Search** | Google News RSS | Free fallback if DuckDuckGo is unavailable |
| **Config Format** | YAML | Human-readable, easy to edit |
| **Environment Variables** | python-dotenv | Loads API keys from `.env` files |
| **HTTP Client** | requests | Simple, reliable HTTP library |
| **LLM Integration** | Raw HTTP API calls | No heavy SDK dependencies — uses direct REST API calls |
| **Styling** | Custom CSS with glassmorphism | Dark theme, modern UI, no framework bloat |
| **Font** | Inter + JetBrains Mono | Professional typography from Google Fonts |

### Python Dependencies (`requirements.txt`)
```
requests>=2.31.0          # HTTP calls to APIs and web pages
beautifulsoup4>=4.12.0    # Parsing HTML from web pages
feedparser>=6.0.0         # Parsing Google News RSS (fallback search)
pyyaml>=6.0               # Reading config.yaml
python-dotenv>=1.0.0      # Loading .env files with API keys
flask>=3.0.0              # Web server for the UI
flask-cors>=4.0.0         # Allow cross-origin requests
```

---

## 4. How It Works — The Agent Loop

This is the heart of the system. The agent follows a **PLAN → EXECUTE → REFLECT → SYNTHESIZE** cycle, inspired by how a human researcher works.

### Phase 1: Planning 📋
**What happens:** The LLM receives your goal and breaks it into specific search queries.

**Example:**
- Input: *"What is SIP trunking and its benefits?"*
- Output queries:
  1. "What are the benefits of using VoIP services for business communication?"
  2. "How does a traditional landline phone system work compared to SIP trunking?"
  3. "What hardware and software infrastructure is required for SIP trunking?"

**How many queries?** Depends on the research depth setting:
- ⚡ **Quick**: 3 queries
- 🔍 **Detailed**: 5 queries
- 🏗️ **Exhaustive**: 8 queries

### Phase 2: Executing 🔍
**What happens:** For each query, the agent:
1. **Searches** DuckDuckGo → gets 5 results (title, URL, snippet)
2. **Extracts** full text from the top 2-3 web pages using BeautifulSoup
3. **Analyzes** the combined search snippets + extracted content using the LLM

The LLM receives the search results and web content, then produces a structured analysis with key findings, technical details, and identified gaps.

### Phase 3: Reflecting 🤔
**What happens:** The LLM evaluates all research collected so far and scores it:
- **Completeness** (1-10): Does the research cover the goal?
- **Depth** (1-10): Are there enough technical specifics?
- **Gaps**: What's missing?
- **Verdict**: `MORE` (do another iteration) or `SUFFICIENT` (proceed to report)

If the verdict is `MORE` and the average score is below 8/10, the agent generates 1-2 new search queries and loops back to Phase 2.

**Maximum iterations:** Controlled by `max_iterations` in config (default: 3).

### Phase 4: Synthesizing 📝
**What happens:** The LLM receives ALL findings from all iterations and writes a comprehensive Markdown report with:
- Executive Summary
- Key Findings
- Recommendations
- Sources & References

The report is automatically saved to the `outputs/` directory.

---

## 5. Project Structure

```
autonomous-agent/
│
├── agent/                          # 🧠 Core agent logic
│   ├── __init__.py                 # Package init, version number
│   ├── core.py                     # Main agent loop (PLAN→EXECUTE→REFLECT→SYNTHESIZE)
│   ├── planner.py                  # Breaks goals into search queries
│   ├── executor.py                 # Runs searches, extracts content, analyzes
│   ├── reflector.py                # Evaluates research quality, decides to loop
│   ├── memory.py                   # Working memory — stores state across the loop
│   ├── config.py                   # Configuration loader with model-aware settings
│   ├── prompts.py                  # All LLM prompt templates (full + compact)
│   │
│   ├── providers/                  # 🔌 LLM Provider adapters
│   │   ├── __init__.py             # Provider factory (get_provider)
│   │   ├── base.py                 # Abstract base class for all providers
│   │   ├── ollama.py               # Ollama (local, free) with streaming
│   │   ├── openai_provider.py      # OpenAI API (GPT-4, GPT-3.5)
│   │   ├── anthropic_provider.py   # Anthropic Claude API
│   │   └── google_provider.py      # Google Gemini API
│   │
│   └── tools/                      # 🔧 Research tools
│       ├── __init__.py             # Package init
│       ├── web_search.py           # DuckDuckGo search + Google RSS fallback
│       └── content_extractor.py    # Web page text extraction
│
├── web/                            # 🌐 Web UI
│   ├── server.py                   # Flask server with SSE streaming
│   ├── app.js                      # Frontend JavaScript (UI logic)
│   ├── index.html                  # HTML structure
│   └── style.css                   # CSS styling (dark theme, glassmorphism)
│
├── outputs/                        # 📄 Generated reports (auto-created)
├── config.yaml                     # ⚙️ Main configuration file
├── .env.example                    # 🔑 Template for API keys
├── requirements.txt                # 📦 Python dependencies
├── run.py                          # 🖥️ CLI entry point
└── README.md                       # 📖 Project README
```

---

## 6. Module-by-Module Deep Dive

### 6.1 Core Agent (`core.py`)

**Purpose:** This is the "brain" — the main orchestrator that runs the entire research cycle.

**Class: `AutonomousAgent`**

| Method | What It Does |
|--------|-------------|
| `__init__(config)` | Initializes the agent: loads config, creates LLM provider, creates sub-agents (Planner, Executor, Reflector), sets up working memory, detects compact mode |
| `set_log_callback(fn)` | Registers a function to call for real-time logging. The Web UI and CLI both use this to display live progress |
| `_log(phase, message)` | Internal logger — writes to memory AND calls the callback (if set) |
| `run(goal) → str` | **The main loop.** Plans → Executes → Reflects → Loops? → Synthesizes → Returns the report as a string |
| `_generate_report(goal) → str` | Generates the final Markdown report: first creates a title, then uses the report prompt with all findings |
| `save_report(report, filename) → str` | Saves the report as a `.md` file in the outputs directory. Auto-generates filename from the goal + timestamp |
| `get_status() → dict` | Returns the current agent state as a dictionary (used by the UI's `/api/status` endpoint) |

**Key Design Decisions:**
- The `compact` flag is set at init time based on `config.small_model_mode` — it cascades to all sub-agents
- The executor receives config-driven parameters (max pages, max content, max tokens)
- Logging is dual-track: memory stores it for state, callback sends it to UI in real-time

---

### 6.2 Planner (`planner.py`)

**Purpose:** Takes a high-level goal and breaks it into specific, searchable web queries.

**Class: `Planner`**

| Method | What It Does |
|--------|-------------|
| `__init__(llm)` | Takes the LLM provider instance |
| `create_plan(goal, depth, num_tasks, compact) → List[str]` | Sends the planning prompt to the LLM, parses the response into individual queries. Filters duplicates and queries that are too short (<10 chars) |

**How it works internally:**
1. Maps depth to number of tasks: `quick`→3, `detailed`→5, `exhaustive`→8
2. Selects compact or full planning prompt
3. Sends to LLM with `temperature=0.4` (low randomness for consistent plans)
4. Parses response line-by-line, strips numbering/bullets
5. Deduplicates and limits to `num_tasks`

---

### 6.3 Executor (`executor.py`)

**Purpose:** Runs the actual research — searching, extracting web content, and analyzing with the LLM.

**Class: `Executor`**

| Parameter | Default (Full) | Default (Compact) | Purpose |
|-----------|---------------|-------------------|---------|
| `max_search_results` | 5 | 5 | How many DuckDuckGo results to fetch |
| `max_pages` | 3 | 2 | How many web pages to extract full text from |
| `max_content_chars` | 6,000 | 2,000 | Max chars of web content sent to LLM |
| `max_analysis_tokens` | 4,096 | 500 | Max tokens in LLM analysis response |
| `compact_mode` | False | True | Use compact prompts |

| Method | What It Does |
|--------|-------------|
| `execute_query(query) → Dict` | The core method: Search → Extract → Analyze. Returns `{query, analysis, sources}` |
| `execute_all(queries) → List[Dict]` | Runs `execute_query` for each query sequentially |
| `set_logger(fn)` | Sets the logging function |

**Inside `execute_query(query)`:**
1. **Search**: Calls `WebSearchTool.search(query)` → gets up to 5 results
2. **Format snippets**: Truncates snippets to 100 chars (compact) or 300 chars (full)
3. **Extract content**: Calls `ContentExtractorTool.extract_multiple()` on top URLs
4. **Build context**: Combines search snippets + extracted web content
5. **Truncate**: Cuts web content to `max_content_chars` to stay within token budget
6. **Analyze**: Sends analysis prompt to LLM with `temperature=0.3` (factual, not creative)

---

### 6.4 Reflector (`reflector.py`)

**Purpose:** The agent's "inner critic" — evaluates research quality and decides whether to continue.

**Class: `Reflector`**

| Method | What It Does |
|--------|-------------|
| `evaluate(goal, summary, compact) → Dict` | Sends the reflection prompt, parses the structured response into scores |
| `_parse_reflection(response) → Dict` | Regex-based parser that extracts COMPLETENESS, DEPTH, GAPS, VERDICT, ADDITIONAL_QUERIES from the LLM response |
| `should_continue(reflection, max_iter, current) → bool` | Decision logic: continue if verdict is MORE, queries exist, avg score < 8, and under max iterations |

**Parsed Output Structure:**
```python
{
    "completeness": 8,         # 1-10 score
    "depth": 7,                # 1-10 score
    "gaps": "Missing pricing information",
    "verdict": "SUFFICIENT",   # or "MORE"
    "additional_queries": [],  # new queries if MORE
    "raw": "...",              # raw LLM response
}
```

**Why regex parsing?** Small local models don't reliably produce JSON. The structured format (e.g., `COMPLETENESS: 8`) is much easier for small models to follow, and regex parsing handles minor formatting variations gracefully.

---

### 6.5 Working Memory (`memory.py`)

**Purpose:** The agent's "brain state" — stores everything across the research loop so data flows between phases.

**Class: `WorkingMemory`**

| Attribute | Type | Purpose |
|-----------|------|---------|
| `goal` | str | The user's original research goal |
| `started_at` | str | ISO timestamp of when research started |
| `plan` | List[str] | The list of search queries from the planner |
| `completed_queries` | List[str] | Queries that have been executed |
| `findings` | List[Dict] | Analysis results from each query |
| `reflections` | List[Dict] | Quality evaluation results from each reflection |
| `iteration` | int | Current iteration number |
| `status` | str | Current phase: idle/planning/researching/reflecting/synthesizing/complete |
| `log` | List[Dict] | All timestamped log entries |

| Method | What It Does |
|--------|-------------|
| `reset(goal)` | Clears everything and starts fresh for a new goal |
| `add_log(phase, message)` | Appends a timestamped log entry |
| `add_finding(query, analysis, sources)` | Stores a research finding and marks the query as completed |
| `add_reflection(completeness, depth, gaps, verdict)` | Stores a reflection result |
| `get_findings_summary() → str` | Formats all findings as a Markdown string (fed to the LLM for report generation) |
| `get_state_dict() → dict` | Returns the full state as a JSON-serializable dictionary (used by the API) |

---

### 6.6 Configuration (`config.py`)

**Purpose:** Loads and manages all configuration from `config.yaml` and `.env` files.

**Class: `Config`**

| Property | Type | Purpose |
|----------|------|---------|
| `provider_name` | str | Active LLM provider (`ollama`, `openai`, `anthropic`, `google`) |
| `provider_config` | dict | Config for the active provider (model, base_url, api_key) |
| `max_iterations` | int | Max reflect-and-iterate cycles (default: 3) |
| `max_search_results` | int | Search results per query (default: 5) |
| `research_depth` | str | `quick`/`detailed`/`exhaustive` |
| `output_dir` | str | Where to save reports (default: `outputs`) |
| `small_model_mode` | bool | **Auto-detected!** True for phi3, gemma2:2b, etc. |
| `max_content_chars` | int | 2,000 (small) or 6,000 (large) |
| `max_pages_to_extract` | int | 2 (small) or 3 (large) |
| `max_report_tokens` | int | 2,000 (small) or 8,000 (large) |
| `max_analysis_tokens` | int | 500 (small) or 4,096 (large) |

**Auto-Detection of Small Models:**
The `SMALL_MODELS` set at the top of the file contains known small model names:
```python
SMALL_MODELS = {
    "phi3", "phi3:latest", "phi3:mini",
    "gemma2:2b", "gemma:2b", "gemma2:2b-instruct",
    "tinyllama", "tinyllama:latest",
    "qwen2:0.5b", "qwen2:1.5b",
    "stablelm2", "stablelm2:1.6b",
    "phi", "phi:latest",
}
```
When the configured model matches any of these, compact mode activates automatically.

---

### 6.7 Prompt Engineering (`prompts.py`)

**Purpose:** All the text templates that tell the LLM what to do. This file is the "instruction manual" for the AI.

Every prompt has **two variants**:
- **Full** — verbose, detailed instructions for powerful models (GPT-4, Claude, Llama3)
- **Compact** — ~60% shorter, simpler instructions for small models (phi3, gemma2:2b)

#### System Prompt
Defines the agent's identity and expertise. Tells the LLM it's a research agent that operates through 5 phases.

```
Full: "You are an Autonomous Research & Solution Architect Agent..." (150 words)
Compact: "You are a research agent. Analyze information and provide clear, factual responses. Be concise." (16 words)
```

#### Planning Prompt
Instructs the LLM to break a goal into search queries.

**Key design:** The prompt says "Return ONLY the queries, one per line. No numbering." — this makes parsing simple and reliable across all models.

#### Analysis Prompt
Instructs the LLM to analyze search results and web content. The full version asks for 4 structured sections (Key Findings, Technical Details, Vendor Insights, Gaps). The compact version simply asks for "key findings in 150 words."

#### Reflection Prompt
Instructs the LLM to evaluate research quality. Uses a **strict structured format** (`COMPLETENESS: [score]`) that's parsed with regex. This format works reliably even with small models.

#### Report Prompt
Instructs the LLM to write the final report. The full version specifies 8 sections (Executive Summary, Background, Key Findings, Architecture, Comparison, Recommendations, Implementation, Conclusion). The compact version has 4 sections (Summary, Key Findings, Recommendations, Sources) and a 600-word limit.

#### Title Prompt
Simple one-liner: generate a short professional title for the report.

#### Helper Functions
| Function | Purpose |
|----------|---------|
| `get_system_prompt(compact)` | Returns the appropriate system prompt |
| `get_planning_prompt(goal, depth, num_tasks, compact)` | Returns formatted planning prompt |
| `get_analysis_prompt(query, results, content, compact)` | Returns formatted analysis prompt |
| `get_reflection_prompt(goal, summary, compact)` | Returns formatted reflection prompt |
| `get_report_prompt(goal, findings, title, compact)` | Returns formatted report prompt |

---

## 7. LLM Providers

The agent uses a **provider pattern** — a common interface that all LLM providers implement. This means you can swap between local and cloud models by changing one line in config.

### 7.1 Base Provider (`base.py`)

**Class: `BaseLLMProvider` (Abstract)**

Every provider must implement:
- `generate(messages, temperature, max_tokens) → str` — Send messages to the LLM, get text back
- `is_available() → bool` — Check if this provider is currently usable

The `messages` format follows the OpenAI standard:
```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is SIP?"},
]
```

### Provider Factory (`__init__.py`)
```python
PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
}

get_provider("ollama", model="phi3", base_url="http://localhost:11434")
```

### 7.2 Ollama — Local Models

**File:** `ollama.py`

- **API:** `http://localhost:11434/api/chat` (Ollama's local REST API)
- **Streaming:** ✅ Enabled — reads response token-by-token as they're generated
- **Timeout:** 30s connect, 300s per-chunk read (resets with each token)
- **Default model:** `llama3`
- **No API key needed** — completely free and private

**How streaming works:**
Instead of waiting for the entire response (which could take 5+ minutes on CPU), the request uses `stream=True`. Each incoming line is a JSON chunk with a single token. The method accumulates tokens until Ollama signals `"done": true`.

**Additional methods:**
- `list_models() → List[str]` — Queries Ollama for all installed models (used by the UI dropdown)

### 7.3 OpenAI

**File:** `openai_provider.py`

- **API:** `https://api.openai.com/v1/chat/completions`
- **Default model:** `gpt-4o-mini`
- **API key:** `OPENAI_API_KEY` from `.env`
- **Also works with:** Groq, Together AI, LM Studio, Azure OpenAI (any OpenAI-compatible API)

### 7.4 Anthropic Claude

**File:** `anthropic_provider.py`

- **API:** `https://api.anthropic.com/v1/messages`
- **Default model:** `claude-3-5-sonnet-20241022`
- **API key:** `ANTHROPIC_API_KEY` from `.env`
- **Note:** Anthropic requires the system message to be passed as a separate `system` field (not in the `messages` array). The provider handles this conversion automatically.

### 7.5 Google Gemini

**File:** `google_provider.py`

- **API:** `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- **Default model:** `gemini-2.0-flash`
- **API key:** `GOOGLE_API_KEY` from `.env`
- **Note:** Gemini uses a different message format (`contents` with `parts`). The provider converts from OpenAI-style messages automatically.

---

## 8. Tools

### 8.1 Web Search (`web_search.py`)

**Class: `WebSearchTool`**

**Primary search:** DuckDuckGo HTML scraping
- No API key required
- Uses a Chrome User-Agent to avoid blocking
- Parses the HTML response with BeautifulSoup to extract results
- Handles redirect URLs (DDG wraps URLs in `uddg=` redirects)

**Fallback search:** Google News RSS
- Used only if DuckDuckGo returns no results
- Uses the `feedparser` library to parse the RSS feed

**Output format:**
```python
[
    {
        "title": "What is SIP Trunking? - Twilio",
        "url": "https://www.twilio.com/docs/sip-trunking",
        "snippet": "SIP trunking allows you to connect..."
    },
    # ... up to max_results
]
```

### 8.2 Content Extractor (`content_extractor.py`)

**Class: `ContentExtractorTool`**

Turns a web page URL into clean, readable text.

**How it works:**
1. Fetches the page with a 15-second timeout
2. Skips non-HTML responses and DuckDuckGo redirect URLs
3. Removes noise: `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`, `<form>`, `<iframe>`, `<svg>`, `<button>`, `<input>`
4. Finds the main content area (tries `<main>`, `<article>`, or a `<div>` with "content" in its class/id)
5. Extracts paragraphs (`<p>`, `<h1>`-`<h4>`, `<li>`, `<td>`) for clean text
6. Falls back to full text if paragraphs yield < 100 characters
7. Filters out tiny lines (< 10 chars) to remove navigation artifacts
8. Truncates to `max_chars`

**`extract_multiple(urls, max_chars_per_page)`** — Extracts text from multiple URLs. Returns a dict of `{url: content}`.

---

## 9. Web UI

### 9.1 Flask Server (`server.py`)

**Purpose:** A lightweight web server that serves the UI and provides API endpoints.

**Global State (`agent_state`):**
```python
{
    "running": False,          # Is the agent currently executing?
    "agent": None,             # The AutonomousAgent instance
    "log_queue": None,         # Queue for SSE log streaming
    "report": None,            # The generated report (content + filepath)
    "error": None,             # Any error message
    "stop_event": None,        # threading.Event for graceful cancellation
}
```

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serves `index.html` |
| `/api/providers` | GET | Returns available providers, their models, and Ollama status |
| `/api/run` | POST | Starts the agent with a goal. Runs in a background thread |
| `/api/stop` | POST | Gracefully stops a running agent by setting the stop event |
| `/api/stream` | GET | **SSE endpoint** — streams log entries in real-time |
| `/api/status` | GET | Returns current agent status, state, and report |
| `/api/reports` | GET | Lists all saved reports in the outputs directory |
| `/api/reports/<filename>` | GET | Returns a specific report's content |

**Threading Model:**
The agent runs in a `daemon` thread so the Flask server remains responsive. A `queue.Queue` bridges the agent thread and the SSE response generator. The `threading.Event` (stop_event) allows graceful cancellation.

**SSE Streaming (`/api/stream`):**
```
Client connects → server pulls from log_queue → sends as SSE events
Each event: data: {"phase": "search", "message": "🔍 Searching: ...", "time": 1234567890}
End signal: data: {"phase": "done", "report": "...", "filepath": "..."}
```

### 9.2 Frontend (`app.js`)

**Purpose:** All the interactive logic for the web UI.

| Function | What It Does |
|----------|-------------|
| `initApp()` | Initializes the app on page load — fetches providers, starts particles |
| `loadProviders()` | Calls `/api/providers` and populates the dropdowns |
| `selectProvider(name)` | Switches the provider and loads its models |
| `setDepth(level)` | Sets research depth (quick/detailed/exhaustive) |
| `startAgent()` | Sends the goal to `/api/run`, starts SSE stream |
| `stopAgent()` | Calls `/api/stop` to gracefully stop the agent |
| `connectStream()` | Opens an EventSource to `/api/stream` for real-time logs |
| `handleStreamEvent(data)` | Processes each SSE event — adds log entries, updates phase tracker |
| `addLogEntry(phase, message)` | Creates a DOM element for each log entry with phase badge and timestamp |
| `updatePhaseTracker(phase)` | Highlights the current phase in the Plan → Research → Reflect → Report tracker |
| `showReport(markdown)` | Renders the markdown report in the right panel |
| `renderMarkdown(text)` | Simple markdown-to-HTML converter (headers, bold, lists, tables, code blocks) |
| `copyReport()` | Copies the raw report to clipboard |
| `downloadReport()` | Downloads the report as a `.md` file |
| `createParticles()` | Creates floating animated dots in the background |
| `toggleReportModal()` | Opens report as a modal overlay on small screens |
| `updateUIState(state)` | Updates button states, status dot, and spinner |

### 9.3 HTML Structure (`index.html`)

**Three-panel layout:**
1. **Left panel (Mission Control):** Provider selector, model dropdown, depth buttons, goal textarea, launch/stop buttons, example chips
2. **Center panel (Agent Thought Process):** Phase tracker (Plan → Research → Reflect → Report), iteration counter, scrollable log entries
3. **Right panel (Generated Report):** Report display with copy/download buttons, empty state placeholder

### 9.4 Styling (`style.css`)

**Design System:**
- **Theme:** Dark purple/blue glassmorphism
- **Background:** Gradient with floating blurred orbs + particle dots
- **Panels:** Semi-transparent with blur backdrop, subtle borders
- **Phase badges:** Color-coded (PLAN=blue, SEARCH=yellow, ANALYZE=purple, REFLECT=green, etc.)
- **Responsive:** Collapses to single column on mobile, report panel becomes modal on screens < 1200px
- **Animations:** Floating background orbs, particle drift, pulse on status dot, slide-in for modals

---

## 10. CLI Interface (`run.py`)

**Purpose:** Run the agent from the command line with colorful terminal output.

**Usage:**
```bash
# Direct goal
python run.py "What is SIP trunking?"

# With options
python run.py --provider openai --model gpt-4o --depth exhaustive "Compare Avaya vs Genesys"

# Interactive (prompts for goal)
python run.py
```

**CLI Arguments:**
| Flag | Short | Purpose |
|------|-------|---------|
| `goal` | — | Research goal (positional) |
| `--provider` | `-p` | Override provider (ollama/openai/anthropic/google) |
| `--model` | `-m` | Override model name |
| `--depth` | `-d` | Override depth (quick/detailed/exhaustive) |
| `--config` | `-c` | Config file path (default: config.yaml) |
| `--output` | `-o` | Output filename for the report |

**Terminal Output:** Uses ANSI color codes for beautiful, color-coded phase labels. Each log entry shows `[timestamp] [PHASE] message` with appropriate colors.

---

## 11. Configuration & Customization

### `config.yaml` — Main Configuration

```yaml
# Which LLM to use
provider: ollama                    # Options: ollama, openai, anthropic, google

# Ollama settings (free, local)
ollama:
  base_url: http://localhost:11434
  model: llama3

# OpenAI settings
openai:
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini

# Anthropic settings
anthropic:
  model: claude-3-5-sonnet-20241022

# Google Gemini settings
google:
  model: gemini-2.0-flash

# Agent behavior
agent:
  max_iterations: 3                 # Max research-reflect loops
  max_search_results: 5             # Search results per query
  research_depth: detailed          # quick (3) | detailed (5) | exhaustive (8)
  # small_model_mode: true          # Uncomment to force compact mode

# Output settings
output:
  directory: outputs
  format: markdown
```

### `.env` — API Keys

```bash
# Copy .env.example to .env and fill in your keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=AIza-your-key-here
```

---

## 12. Making It Your Own — Customization Guide

### Research Any Topic (Not Just Contact Centers)

The default system prompt mentions Contact Center technologies, but this agent can research **anything**. To customize:

1. **Edit `prompts.py`** — Change `AGENT_SYSTEM_PROMPT` to match your domain:
```python
AGENT_SYSTEM_PROMPT = """You are an Autonomous Research Agent.
Your expertise covers [YOUR DOMAIN HERE].
You operate autonomously by planning, researching, analyzing, reflecting, and synthesizing."""
```

2. **Edit the Planning Prompt** — Remove the Contact Center-specific rules:
```python
# Change this line in PLANNING_PROMPT:
# "For Contact Center/VoIP topics, include vendor-specific queries"
# To:
# "For [YOUR DOMAIN], include [YOUR SPECIFIC ANGLES]"
```

3. **Edit the Analysis Prompt** — Change the analyst role:
```python
# Change: "research analyst specializing in Contact Center"
# To: "research analyst specializing in [YOUR FIELD]"
```

### Change Research Depth
```yaml
# In config.yaml:
agent:
  research_depth: exhaustive  # 8 queries instead of 5
  max_iterations: 5           # Allow more reflect-iterate loops
  max_search_results: 10      # More search results per query
```

### Use a Different LLM
```yaml
# Switch to Google Gemini (fast, free tier available):
provider: google
google:
  model: gemini-2.0-flash
```

### Customize the Report Format
Edit `REPORT_PROMPT` in `prompts.py` to change sections. For example, to add a "Competitive Landscape" section:
```python
## Competitive Landscape
Analyze competitors, market positioning, and differentiation strategies.
```

### Add a New LLM Provider
1. Create `agent/providers/my_provider.py`
2. Extend `BaseLLMProvider`
3. Implement `generate()` and `is_available()`
4. Register in `agent/providers/__init__.py`:
```python
from .my_provider import MyProvider
PROVIDERS["my_provider"] = MyProvider
```

### Add New Tools
Create a new tool in `agent/tools/`:
```python
class MyTool:
    def run(self, input_data):
        # Your tool logic here
        return result
```
Then import and use it in `executor.py`.

---

## 13. API Reference

### POST `/api/run`
Start the agent.

**Request body:**
```json
{
    "goal": "What is SIP trunking?",
    "provider": "ollama",
    "model": "phi3:latest",
    "depth": "quick"
}
```

**Response:**
```json
{ "status": "started", "goal": "What is SIP trunking?" }
```

### POST `/api/stop`
Stop a running agent gracefully.

**Response:**
```json
{ "status": "stopping" }
```

### GET `/api/stream`
SSE endpoint for real-time log streaming.

**Event format:**
```
data: {"phase": "plan", "message": "📋 PHASE 1: PLANNING...", "time": 1234567890}
data: {"phase": "done", "report": "# Report Title\n...", "filepath": "outputs/report.md"}
```

### GET `/api/providers`
List available LLM providers and their models.

### GET `/api/status`
Get current agent state (running, iteration, findings count, etc.).

### GET `/api/reports`
List all saved reports in the outputs directory.

### GET `/api/reports/<filename>`
Get a specific report's full content.

---

## 14. Performance Optimization — Small Model Mode

When using small models like phi3 (3.8B) or gemma2:2b (2B) on CPU, the agent auto-enables **COMPACT mode** which:

| Setting | Full Mode (GPT-4, Llama3) | Compact Mode (phi3, gemma2:2b) |
|---------|--------------------------|-------------------------------|
| Prompt style | Verbose, multi-section | Short, focused |
| Web pages extracted | 3 | 2 |
| Content per page | 3,000 chars | 1,500 chars |
| Content to LLM | 6,000 chars | 2,000 chars |
| Snippet length | 300 chars | 100 chars |
| Analysis tokens | 4,096 | 500 |
| Report tokens | 8,000 | 2,000 |
| Report length | 1,500+ words | 600 words |
| System prompt | 150 words | 16 words |

**The 6 Optimization Principles:**
1. 🧹 Reduce input tokens — fewer pages, less content, truncated snippets
2. ✂️ Shorter prompts — compact variants that small models follow better
3. 🔄 Streaming — Ollama reads tokens as they're generated (no all-or-nothing timeout)
4. ⚙️ Model-aware config — auto-detects small models and adjusts everything
5. 📉 Realistic expectations — don't ask a 2B model for a 1,500-word report
6. ⏱ Adaptive timeouts — 300s per-chunk timeout that resets with each token

---

## 15. Setup & Installation

### Prerequisites
- **Python 3.10+** installed
- **Ollama** installed and running (for local models) — [Download Ollama](https://ollama.com)

### Step-by-Step

```bash
# 1. Clone the repo
git clone https://github.com/your-repo/autonomous-agent.git
cd autonomous-agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Set up API keys for cloud providers
cp .env.example .env
# Edit .env and add your keys

# 6. (Optional) Pull an Ollama model
ollama pull llama3
# or for a smaller, faster model:
ollama pull phi3

# 7a. Run with Web UI
python web/server.py
# Open http://localhost:5000

# 7b. Or run from CLI
python run.py "Your research question here"
```

---

## 16. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `UnicodeDecodeError: charmap codec can't decode` | Windows encoding issue reading `config.yaml` | Fixed in code — uses `encoding='utf-8'` |
| `ConnectionError: Cannot connect to Ollama` | Ollama isn't running | Run `ollama serve` in a terminal |
| `Timeout` during analysis | Model too slow for the input size | Use "Quick" depth, or switch to a faster model/provider |
| `Extracted content from 0 pages` | Web pages blocked the scraper | Normal — the agent falls back to search snippets |
| `500 Internal Server Error` | Config parsing or provider error | Check the terminal running `server.py` for the traceback |
| UI shows `Error` state | Backend exception | Check server logs, most common: missing API key or Ollama not running |
| Report is too short | Using a small model | Expected — compact mode limits output. Use GPT-4 or Gemini for longer reports |

---

> **Built with ❤️ as a learning project in autonomous AI agents.**
> The entire codebase is designed to be readable, modular, and hackable — fork it, change the prompts, add new tools, and make it your own.
