# NanoDeepResearch

A lightweight, practical **deep-research agent** that combines a **ReAct-style loop** with **web search + source visiting** to answer information-seeking questions with higher confidence.

- **LLM via OpenRouter**
- **Search & extraction via Tavily**
- Designed for fast experimentation: swap models, run the same query, compare results, and inspect logs.

---

## Why DeepResearch

Typical “search-only” workflows often return plausible but wrong answers. DeepResearch is built around a simple idea:

> Search widely → visit key sources → verify details → produce a grounded answer.

It’s intentionally small and hackable, meant for:
- deep information-seeking tasks,
- comparing model behaviors on the same research question,
- iterating on prompts/tools quickly.

---

## How it works (high level)

DeepResearch runs a ReAct-like loop:
1. **Plan / Think** about what to search
2. Call **`search`** (Tavily) to get candidate sources
3. Call **`visit`** (Tavily extract) to read and verify critical pages
4. Refine until it can answer confidently
5. Save logs to `output/` for inspection and benchmarking

---

## Features

- **Two-tool research workflow**
  - `search`: multi-query web search
  - `visit`: content extraction from URLs for verification
- **Model-agnostic (via OpenRouter)**: evaluate different LLMs using the same tool chain
- **Traceable runs**: logs saved under `output/` so you can compare reasoning/tool usage
- **Small codebase**: easy to customize prompts, tool formatting, and loop behavior

---

## Quick Start

### 1) Requirements

- Python **3.10+** recommended

Install dependencies:

```bash
pip install -r requirements.txt
pip install python-dotenv tiktoken
````

### 2) Configure environment variables

Create a `.env` in the project root:

```bash
# OpenRouter API (LLM)
OPENAI_API_KEY="your-openrouter-key"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_MODEL="as-you-wish"  # example: deepseek/deepseek-v3.2

# Tavily API (Search + Web Extract)
TAVILY_API_KEY="your-tavily-key"
```

### 3) Run the sample

```bash
cd inference
python3 test_query.py
```

To change the question, edit `inference/test_query.py`:

```python
test_query = "Your research question here"
```

Outputs and run logs are written to `output/`.

---

## Project layout

```text
DeepResearch/
├── .env                 # Local config (not committed)
├── requirements.txt     # Dependencies
├── inference/
│   ├── react_agent.py   # ReAct agent loop (core)
│   ├── prompt.py        # System prompts
│   ├── tool_search.py   # Tavily /search wrapper
│   ├── tool_visit.py    # Tavily /extract wrapper
│   └── test_query.py    # Example runner
└── output/              # Logs and run artifacts
```

---

## Tools

| Tool     | Provider | Endpoint   | Purpose                                      |
| -------- | -------- | ---------- | -------------------------------------------- |
| `search` | Tavily   | `/search`  | Find relevant sources using multiple queries |
| `visit`  | Tavily   | `/extract` | Read/parse selected URLs to verify key facts |

**Recommendation:** For fact-sensitive questions, don’t stop at search—use `visit` to confirm.

---

## Model support (OpenRouter)

DeepResearch works with OpenRouter-hosted models that expose an OpenAI-compatible interface.

Common examples:

* `alibaba/tongyi-deepresearch-30b-a3b`
* `deepseek/deepseek-v3.2`
* `qwen/qwen3-32b`
* …and other OpenRouter models

---

## Example: Model comparison (2026-01-20)

DeepResearch was used to evaluate multiple models on the same research prompt.

**Test question (CN):**
A China national football team match: conceded first, equalized by a player with surname “Su” (宿), later involved a penalty, ended in a draw. Which match was it?

**Ground-truth answer:**
**China vs South Korea, 2–2**, AFC Asian Cup group stage, **Oct 13, 2000**.

### Results summary

| Model                                 | Correct | Tool usage         | Notes                                                                        |
| ------------------------------------- | ------- | ------------------ | ---------------------------------------------------------------------------- |
| `alibaba/tongyi-deepresearch-30b-a3b` | ✅       | `search` + `visit` | Fast and accurate; verified via visited sources                              |
| `deepseek/deepseek-v3.2`              | ✅       | `search` + `visit` | Correct but required more iterations; tool-call formatting needed adaptation |
| `qwen/qwen3-32b`                      | ❌       | `search` only      | Identified the key name but settled on the wrong match; lacked verification  |

### Takeaways

* **Best overall:** `alibaba/tongyi-deepresearch-30b-a3b` (strong at pinpointing + verifying)
* **Solid but noisier:** `deepseek/deepseek-v3.2` (correct, but more retries / formatting friction)
* **Not recommended for this task:** `qwen/qwen3-32b` (search-only outcome drifted)

Related logs (relative paths):

* `./test_tongyi-deepresearch-30b-a3b_20260120_084633.log`
* `./test_qwen3-32b.log`
* `./test_deepseek-v3.2.log`

---

## Repo snapshot (for reference)

As of **2026-01-20**, the project is intentionally small:

* ~8 files total
* ~500 lines of Python across the agent/tools

(These numbers will evolve as the repo grows.)

---

## License

See [LICENSE](LICENSE).

