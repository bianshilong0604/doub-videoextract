---
name: Bug report
about: Report a problem with extraction, summarization, or the CLI
title: "[Bug] <short summary>"
labels: bug
assignees: ''
---

## Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Command run: `python main.py "<URL>" --config config.json ...`
2. Input URL (redact if private):
3. What you expected:
4. What actually happened:

## Error Output

Paste the full traceback or relevant log lines. Use a code block.

```
<paste error here>
```

## Environment

- OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [output of `python --version`]
- videoextract commit / version: [git rev-parse --short HEAD or release tag]
- Installed optional deps: [ ] douyin-tiktok-scraper [ ] faster-whisper [ ] yt-dlp
- AI provider: [DeepSeek / OpenAI / GLM / SenseNova / other]

## Configuration

Redact `api_key`. Paste relevant parts of `config.json`:

```json
{
  "ai_api": { "base_url": "...", "model": "..." },
  "transcribe": { "enabled": ..., "method": "..." }
}
```

## Reproducibility

- [ ] Reproduces every time
- [ ] Intermittent
- [ ] Happened once

## Additional Context

Anything else relevant — screenshots, related issues, recent changes you made, etc.

## Checklist

- [ ] I have redacted API keys, cookies, and personal data from this report
- [ ] I have searched existing issues and this is not a duplicate
- [ ] I have tried the latest `main` branch
