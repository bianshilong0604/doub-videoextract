# douB-videoextract

> 智能视频/图文内容提取与 AI 总结工具
> A Python CLI to extract content from Douyin / Bilibili and generate detailed AI summaries.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 简介 / Overview

**中文**：从抖音、B 站等平台一键抓取视频或图文内容，自动调用任意 OpenAI 兼容 API（DeepSeek、智谱 GLM、SenseNova、OpenAI 等）生成 5000-7000 字的超详细分析报告，输出 Markdown + JSON。

**English**: One-command extraction of video / image-text posts from Douyin and Bilibili, with detailed AI summaries (5,000–7,000 words, no token cap) via any OpenAI-compatible API. Outputs Markdown + JSON.

## Features / 功能特性

- **Multi-platform** — Douyin (video & image-text), Bilibili (video + official subtitles)
- **3-layer Douyin fallback** — `douyin-tiktok-scraper` → `yt-dlp` → HTML parsing, so a single endpoint break does not kill the run
- **Provider-agnostic AI** — any OpenAI-compatible chat-completions endpoint
- **Detail-heavy prompts** — no `max_tokens` cap; produces structured deep analysis (summary, 8–10 key points, background, examples, actionable steps, insights, audience, value)
- **Optional ASR** — local `faster-whisper` or cloud API for videos without subtitles
- **Batch mode** — feed a `.txt` of URLs and get a consolidated report
- **Markdown + JSON output** — read it, ingest it, pipe it

## Supported Platforms / 支持平台

| Platform | Video | Image-text | Subtitles | Notes |
|----------|:-----:|:----------:|:---------:|-------|
| Douyin (抖音)   | Yes | Yes | via ASR | 3-layer fallback |
| Bilibili (B 站) | Yes | —   | Native + ASR | Uses `bilibili-api-python` |

## Quick Start / 快速开始

```bash
git clone https://github.com/<your-org>/videoextract.git
cd videoextract
./setup.sh                                           # installs deps, creates .env / config.json

# edit config.json and set ai_api.api_key
python main.py "https://v.douyin.com/xxx" --config config.json
```

Open `output/` — your `{title}.md` and `{title}.json` are there.

See [CLAUDE.md](CLAUDE.md) for full architecture and command reference.

## Prerequisites / 环境要求

- Python 3.8+
- pip
- (Optional) `ffmpeg` on PATH if you enable local ASR

## Installation / 安装

```bash
# 1. Clone
git clone https://github.com/<your-org>/videoextract.git
cd videoextract

# 2. Run setup (preferred)
./setup.sh

# --- or manually ---
pip install -r requirements.txt
pip install douyin-tiktok-scraper      # optional, recommended for Douyin
pip install faster-whisper             # optional, only if you enable ASR
cp config.example.json config.json
```

## Configuration / 配置

Copy the template and fill in your AI API key:

```bash
cp config.example.json config.json
```

```json
{
  "ai_api": {
    "api_key": "YOUR_API_KEY_HERE",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  },
  "transcribe": {
    "enabled": false,
    "method": "auto",
    "whisper_model": "base",
    "language": "zh"
  },
  "output": {
    "dir": "./output",
    "format": "markdown"
  }
}
```

### Configuration reference

| Key | Required | Default | Description |
|-----|:--------:|---------|-------------|
| `ai_api.api_key` | Yes | — | API key for the LLM provider |
| `ai_api.base_url` | Yes | `https://api.deepseek.com/v1` | OpenAI-compatible endpoint |
| `ai_api.model` | Yes | `deepseek-chat` | Model name (`gpt-4o`, `glm-4`, etc.) |
| `transcribe.enabled` | No | `false` | Enable ASR when video has no subtitles |
| `transcribe.method` | No | `auto` | `auto` / `local` / `api` |
| `transcribe.whisper_model` | No | `base` | `tiny` / `base` / `small` / `medium` / `large` |
| `transcribe.language` | No | `zh` | ASR language hint |
| `output.dir` | No | `./output` | Output directory |
| `output.format` | No | `markdown` | Currently only `markdown` |

### Compatible AI providers / 兼容的 AI 服务商

| Provider | `base_url` | Example model |
|----------|------------|---------------|
| DeepSeek (recommended) | `https://api.deepseek.com/v1` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |
| SenseNova | `https://token.sensenova.cn/v1` | `deepseek-v4-flash` |

`.env.example` shows the equivalent environment-variable layout.

## Usage / 使用示例

```bash
# Single URL
python main.py "https://v.douyin.com/xxx" --config config.json

# Bilibili
python main.py "https://www.bilibili.com/video/BVxxxxxxxxxx" --config config.json

# Batch — urls.txt is one URL per line, blank lines / # comments allowed
python main.py urls.txt --batch --config config.json

# Extraction only, skip the AI summary
python main.py "URL" --no-summary --config config.json

# Custom output directory
python main.py "URL" --config config.json --output ./reports

# Interactive mode (paste URLs one at a time, type 'q' to quit)
python main.py --config config.json
```

### Python API / 在代码中调用

```python
from extractors.douyin_enhanced import EnhancedDouyinExtractor
from extractors import BilibiliExtractor
from processors import Summarizer

extractor = EnhancedDouyinExtractor()
content = extractor.extract("https://v.douyin.com/xxx")

summarizer = Summarizer({
    "api_key": "YOUR_KEY",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
})
summary = summarizer.summarize(content)
print(summarizer.format_summary_markdown(summary))
```

## Output Format / 输出格式

For each URL, two files land in `output/`:

- `{title}.md` — readable report
  - Metadata (platform, type, author, duration, publish time)
  - Statistics (views / likes / comments / shares)
  - Description, text content, subtitles
  - AI deep analysis: summary, 8–10 key points, background, core content, examples, actionable steps, insights, keywords, audience, value, learning path, difficulty, time-value
- `{title}.json` — full structured data: `{ "content": ContentData, "summary": {...} }`

Batch mode additionally writes `output/batch_report.md` summarizing success / failure per URL.

## Project Structure / 项目结构

```
videoextract/
├── main.py                          # CLI entry, ContentExtractorApp, batch report
├── config.example.json              # Config template
├── .env.example                     # Env-var alternative
├── requirements.txt                 # Core dependencies
├── setup.sh                         # One-command bootstrap
├── CLAUDE.md                        # Context for Claude Code
├── extractors/
│   ├── base.py                      # ContentData + BaseExtractor
│   ├── bilibili.py                  # Bilibili extractor
│   ├── douyin.py                    # Basic Douyin extractor
│   └── douyin_enhanced.py           # 3-layer Douyin extractor
├── processors/
│   ├── summarizer.py                # AI summarizer (OpenAI-compatible)
│   ├── transcriber.py               # ASR (cloud API mode)
│   └── transcriber_enhanced.py      # ASR via faster-whisper
├── utils/
│   └── file_utils.py                # sanitize_filename, save_json, read_urls
└── output/                          # Generated reports (gitignored)
```

## Using with Claude Code / 配合 Claude Code 使用

This repo ships with a [`CLAUDE.md`](CLAUDE.md) — Claude Code reads it on startup and instantly knows the architecture, key files, and commands.

```bash
claude    # in the project root — CLAUDE.md is picked up automatically
```

Try prompts like:

- "Add support for Xiaohongshu in `extractors/`"
- "Switch the summarizer to use streaming responses"
- "Write tests for the 3-layer Douyin fallback"

## Contributing / 贡献

PRs and issues welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, code style, and how to add a new platform extractor.

Bug reports → [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
Feature requests → [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)

## License / 许可证

[MIT](LICENSE) — Copyright (c) 2026 videoextract contributors.

## Disclaimer / 免责声明

This tool is for personal study and content archiving. Respect each platform's Terms of Service and the original creators' copyright. Do not use the extracted content for commercial redistribution without permission.

本工具仅供个人学习与内容归档使用。请遵守各平台服务条款及原作者版权，未经许可不得用于商业转载。
