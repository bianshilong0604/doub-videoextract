# videoextract — Video Content Extractor & AI Summarizer

A multi-platform video and image-text content extraction tool with AI-powered summarization. Supports Douyin (TikTok), Bilibili, and extensible to other platforms.

## Features

- Multi-platform video support — Douyin, Bilibili video metadata extraction
- Image-text content extraction — Douyin image posts
- Speech-to-text — optional local Whisper or API-based transcription
- AI summarization — detailed content summaries and key point extraction
- Multiple output formats — Markdown and JSON

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API

Copy the example config and fill in your values:

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "ai_api": {
    "api_key": "your-api-key-here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  },
  "transcribe": {
    "enabled": false,
    "method": "auto",
    "whisper_model": "base"
  },
  "output": {
    "dir": "./output",
    "format": "markdown"
  }
}
```

Alternatively, use environment variables (see `.env.example`).

### 3. Run

```bash
# Single URL
python main.py "https://v.douyin.com/xxx" --config config.json

# Batch processing (URLs in a .txt file, one per line)
python main.py urls.txt --batch --config config.json

# Extract only, no AI summary
python main.py "https://v.douyin.com/xxx" --no-summary

# Interactive mode
python main.py
```

## Supported Platforms

| Platform | Video | Image-text | Subtitles | Notes |
|----------|-------|------------|-----------|-------|
| Douyin   | Yes   | Yes        | Optional  | Requires speech recognition |
| Bilibili | Yes   | No         | Yes       | Official subtitles supported |

## Output

Results are saved to the `output/` directory (configurable):

- `{title}.md` — Markdown with metadata + AI summary
- `{title}.json` — Full structured data

## Project Structure

```
videoextract/
├── main.py                        # Entry point
├── config.example.json            # Config template
├── .env.example                   # Environment variable template
├── requirements.txt               # Dependencies
├── extractors/
│   ├── base.py                    # Base extractor and ContentData model
│   ├── bilibili.py                # Bilibili extractor
│   ├── douyin.py                  # Douyin extractor (basic)
│   └── douyin_enhanced.py         # Douyin extractor (3-layer fallback)
├── processors/
│   ├── summarizer.py              # AI summarizer
│   ├── transcriber.py             # Speech-to-text (basic)
│   └── transcriber_enhanced.py    # Speech-to-text (faster-whisper)
└── utils/
    └── file_utils.py              # File utilities
```

## AI Summary Configuration

The summarizer is compatible with any OpenAI-format API:

- Deepseek (recommended, cost-effective)
- OpenAI
- Any compatible provider

Set `ai_api.base_url` in `config.json` to point to your provider.

## Speech-to-Text

Supports multiple backends:

1. **Local Whisper** (free, via `faster-whisper`)
2. **OpenAI Whisper API** (paid)

Install faster-whisper for local transcription:

```bash
pip install faster-whisper
```

## Python API

```python
from extractors import DouyinExtractor, BilibiliExtractor
from processors import Summarizer

extractor = DouyinExtractor()
content = extractor.extract("https://v.douyin.com/xxx")

summarizer = Summarizer({"api_key": "your-key", "base_url": "...", "model": "..."})
summary = summarizer.summarize(content)
print(summary)
```

## Contributing

Issues and pull requests are welcome.

## License

MIT License
