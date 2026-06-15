# Contributing to videoextract

Thanks for your interest in improving videoextract. This guide covers the development workflow, code style, and how to add a new platform extractor.

## Development Setup

```bash
git clone https://github.com/<your-org>/videoextract.git
cd videoextract
./setup.sh
# edit config.json — set ai_api.api_key
python main.py "https://v.douyin.com/xxx" --config config.json
```

If `setup.sh` is not available on your platform (e.g. plain Windows cmd), do it manually:

```bash
pip install -r requirements.txt
pip install douyin-tiktok-scraper      # optional but recommended
cp config.example.json config.json
```

## Branch & PR Workflow

1. Fork the repo and create a feature branch off `main`:
   ```bash
   git checkout -b feat/my-thing
   ```
2. Make focused commits using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add Xiaohongshu extractor`
   - `fix: handle Bilibili pagination on long videos`
   - `refactor: extract retry helper from douyin_enhanced`
   - `docs: clarify config.json keys`
3. Run a smoke test before pushing:
   ```bash
   python main.py "<a real URL>" --config config.json
   ```
4. Open a PR against `main`. Describe **what** changed, **why**, and how you tested it. Link any related issues.

Keep PRs small and single-purpose where possible. Large PRs get split.

## Code Style

This project favors clarity over cleverness. The existing code reflects the style we want:

- **Python 3.8+** syntax, type hints on public methods
- **Docstrings** for classes and non-trivial methods (Chinese or English, match the surrounding file)
- **`dataclass` for data models** — see `extractors/base.ContentData`
- **Abstract base classes** for extension points — see `BaseExtractor`
- **Functions under ~50 lines**, files under ~800 lines
- **Explicit error handling** — no bare `except:`. Catch the specific exception, log a clear message, return `None` or re-raise as appropriate
- **No mutation of inputs** — return new objects when transforming
- **Print statements with emoji prefixes** for user-facing CLI feedback are part of the project voice (e.g. `print("✅ ...")`, `print("⚠️  ...")`)
- **No hardcoded secrets** — read from `config.json` or env vars

There is no enforced linter today. If you want to format, `black` and `ruff check` with defaults are safe choices.

## Adding a New Platform Extractor

1. Create `extractors/<platform>.py`.
2. Subclass `BaseExtractor` from `extractors/base.py`.
3. Implement:
   - `can_handle(url: str) -> bool` — URL pattern match
   - `extract(url: str) -> Optional[ContentData]` — populate and return a `ContentData`
4. Set `self.platform` to a human-readable name in `__init__`.
5. Register the extractor in `main.py`'s `ContentExtractorApp.__init__` (`self.extractors` list).
6. Export it from `extractors/__init__.py` if it's part of the public surface.
7. Add a row to the "Supported Platforms" table in `README.md`.

If your extractor has multiple data sources (official API, scraper lib, HTML fallback), follow the pattern in `extractors/douyin_enhanced.py` — try each layer in order and return the first success.

## Testing

There is no test suite yet. Contributions that add `pytest` coverage are very welcome — start with `extractors/base.ContentData` and `utils/file_utils`. Until then, please include a manual test plan in your PR description (sample URL + expected behavior).

## Reporting Issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`:

- **Bug**: include the URL, the exact command, the full error output, your Python version, and OS.
- **Feature**: describe the use case before the proposed solution.

Please **redact API keys, cookies, and personal data** from anything you paste.

## Security

If you find a vulnerability (e.g. command injection in URL handling, path traversal in filename sanitization), please open a private security advisory on GitHub instead of a public issue.

## Using Claude Code

The repo ships with `CLAUDE.md`. Run `claude` from the project root and it will read the architecture map, command list, and key files automatically. Good prompts to try:

- "Read `extractors/douyin_enhanced.py` and add a 4th layer using the official Douyin web API."
- "Add a `--json-only` flag to `main.py` that skips Markdown output."
- "Refactor `processors/summarizer.py` to support streaming responses."

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
