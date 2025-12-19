# Tongyi DeepResearch Inference

This repository contains the inference code for **Tongyi DeepResearch**, an agentic large language model designed for long-horizon, deep information-seeking tasks.

## 🚀 Quick Start

### 1. Environment Setup

Recommended Python version: **3.10+**

It is strongly advised to create an isolated environment using `conda` or `virtualenv`.

```bash
# Example with Conda
conda create -n deep_research python=3.10
conda activate deep_research
```

### 2. Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and provide your actual API keys:
   - **SERPER_KEY_ID**: Get your key from [Serper.dev](https://serper.dev/) for web search and Google Scholar
   - **JINA_API_KEYS**: Get your key from [Jina.ai](https://jina.ai/) for web page reading
   - **API_KEY/API_BASE**: OpenAI-compatible API for page summarization from [OpenAI](https://platform.openai.com/)
   - **DASHSCOPE_API_KEY**: Get your key from [Dashscope](https://dashscope.aliyun.com/) for file parsing
   - **SANDBOX_FUSION_ENDPOINT**: Python interpreter sandbox endpoints (see [SandboxFusion](https://github.com/bytedance/SandboxFusion))
   - **MODEL_PATH**: Path to your model weights
   - **DATASET**: Name of your evaluation dataset
   - **OUTPUT_PATH**: Directory for saving results

### 4. Run Inference

The inference scripts are located in the `inference/` directory.

```bash
cd inference
bash run_react_infer.sh
```

**Note:** You may need to modify `run_react_infer.sh` to set the correct `MODEL_PATH`, `DATASET`, and `OUTPUT_PATH`.

## 📂 Project Structure

- `inference/`: Contains the core inference logic and agents.
  - `react_agent.py`: Main ReAct agent implementation.
  - `tool_*.py`: Various tools (search, file parser, python interpreter, etc.).
  - `run_react_infer.sh`: Script to launch the inference.
  - `eval_data/`: Directory for evaluation data and file corpus.
- `requirements.txt`: Python dependencies.
- `.env.example`: Example environment configuration file.

## 📊 Supported Input Formats

The system supports two input file formats: **JSON** and **JSONL**.

**Option 1: JSONL Format (recommended)**
Each line must be a valid JSON object with `question` and `answer` keys:
```json
{"question": "What is the capital of France?", "answer": "Paris"}
```

**Option 2: JSON Format**
A JSON array of objects:
```json
[
  { "question": "What is the capital of France?", "answer": "Paris" }
]
```

**File References:**
If using the file parser tool, prepend the filename to the `question` field and place referenced files in `inference/eval_data/file_corpus/`.
