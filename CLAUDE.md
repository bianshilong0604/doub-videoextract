# CLAUDE.md — Project Instructions

## Project Overview

`videoextract` is a multi-platform video and image-text content extraction tool with AI summarization. It supports Douyin and Bilibili, with a three-layer fallback mechanism for Douyin extraction.

## Setup

```bash
pip install -r requirements.txt
cp config.example.json config.json
# Edit config.json and set your API key
```

## Running

```bash
# Single URL
python main.py "https://v.douyin.com/xxx" --config config.json

# Batch mode
python main.py urls.txt --batch --config config.json

# No AI summary
python main.py "https://v.douyin.com/xxx" --no-summary
```

## Architecture

- `extractors/` — Platform-specific content extractors implementing `BaseExtractor`
- `processors/` — Content processing: AI summarization (`Summarizer`), speech-to-text (`EnhancedTranscriber`)
- `utils/` — Shared file utilities

## Adding a New Platform

1. Create `extractors/yourplatform.py` implementing `BaseExtractor`
2. Implement `can_handle(url)` and `extract(url) -> ContentData`
3. Register in `main.py` inside `ContentExtractorApp.__init__`

## Configuration

All secrets go in `config.json` (gitignored). See `config.example.json` for the schema. Environment variables are also supported via `.env` — see `.env.example`.

## Key Dependencies

- `yt-dlp` — video metadata and audio extraction
- `bilibili-api-python` — Bilibili API
- `douyin-tiktok-scraper` — Douyin scraper (optional, layer 1 fallback)
- `faster-whisper` — local speech-to-text (optional)
- `beautifulsoup4` — HTML parsing fallback
