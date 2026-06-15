# videoextract

**Stack:** Python 3.8+ CLI | **Entry:** `main.py` | **Output:** `./output/`

## What

Smart video and image-text content extractor with AI summarization. Pulls metadata, descriptions, and (when available) subtitles from Douyin and Bilibili links, then generates detailed Markdown + JSON reports via any OpenAI-compatible LLM API.

## Quick Start

```bash
./setup.sh                                              # First-time setup
cp config.example.json config.json                      # Then edit api_key
python main.py "https://v.douyin.com/xxx" --config config.json
```

## Commands

```bash
# Setup
pip install -r requirements.txt                         # Core deps
pip install douyin-tiktok-scraper                       # Optional: layer 1 Douyin
pip install faster-whisper                              # Optional: local ASR
cp config.example.json config.json                      # Then fill in api_key

# Run — single URL
python main.py "https://v.douyin.com/xxx" --config config.json
python main.py "https://www.bilibili.com/video/BVxxx" --config config.json

# Run — batch (one URL per line in urls.txt)
python main.py urls.txt --batch --config config.json

# Run — without AI summary (extraction only)
python main.py "URL" --no-summary --config config.json

# Run — interactive mode (no input arg)
python main.py --config config.json

# Run — custom output directory
python main.py "URL" --config config.json --output ./my-output
```

## Architecture

```
main.py                              Entry — ContentExtractorApp orchestrates
extractors/
  base.py                            ContentData dataclass + BaseExtractor ABC
  douyin_enhanced.py                 3-layer fallback: scraper-lib → yt-dlp → web
  douyin.py                          Basic Douyin extractor (legacy)
  bilibili.py                        Bilibili via bilibili-api-python
processors/
  summarizer.py                      OpenAI-compatible AI summarizer (no token cap)
  transcriber_enhanced.py            faster-whisper based ASR
  transcriber.py                     Basic ASR (cloud API mode)
utils/
  file_utils.py                      sanitize_filename, save_json, read_urls
```

Flow: `main.py` detects platform via `extractor.can_handle(url)`, runs `extract()` to populate `ContentData`. If video and no subtitles, optional `transcriber.transcribe_video_url()` fills them. Then `summarizer.summarize()` calls the chat-completions endpoint with a detail-heavy system prompt and the formatted result is written as `{title}.md` and `{title}.json`.

## Key Files

```
main.py                              CLI parser, ContentExtractorApp, batch report
extractors/base.py                   ContentData (the shared schema all extractors fill)
extractors/douyin_enhanced.py        Production Douyin path with 3-layer fallback
extractors/bilibili.py               Bilibili video + subtitles
processors/summarizer.py             AI prompt + JSON parsing + Markdown formatter
config.example.json                  Config template (copy to config.json)
.env.example                         Env-var alternative
requirements.txt                     Pinned core dependencies
```

## Configuration

Configure via `config.json` (preferred) or environment variables. Copy `config.example.json` to `config.json`, then edit:

| Key | Required | Description |
|-----|----------|-------------|
| `ai_api.api_key` | Yes (for summary) | API key for the LLM provider |
| `ai_api.base_url` | Yes | OpenAI-compatible endpoint, e.g. `https://api.deepseek.com/v1` |
| `ai_api.model` | Yes | Model name, e.g. `deepseek-chat`, `gpt-4o`, `glm-4` |
| `transcribe.enabled` | No | `true` to enable ASR fallback when video has no subtitles |
| `transcribe.method` | No | `auto`, `local` (faster-whisper), or `api` |
| `transcribe.whisper_model` | No | `tiny` / `base` / `small` / `medium` / `large` |
| `transcribe.language` | No | ASR language hint, default `zh` |
| `output.dir` | No | Output directory, default `./output` |
| `output.format` | No | `markdown` (default) |

Compatible AI providers (set `base_url` accordingly): DeepSeek, OpenAI, Zhipu GLM, SenseNova, or any OpenAI-format endpoint.

## Output Format

For each processed URL, two files are written to `output/`:

- `{title}.md` — Human-readable report: metadata, statistics, description, transcript (if any), AI summary, key points, deep analysis, keywords, audience, value
- `{title}.json` — Full structured data: `{ "content": ContentData, "summary": {...} }`

Batch mode also writes `output/batch_report.md` with per-URL success/failure status.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
