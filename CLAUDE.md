# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitHub AI Trending Bot is a Python-based automation that fetches trending AI/LLM repositories from GitHub and pushes formatted reports to Feishu (Lark) via webhook. It runs as a scheduled GitHub Actions workflow (daily at 08:00 Beijing Time).

## Development Commands

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Bot Locally

```bash
# Set required environment variables
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
export GIT_TOKEN="ghp_xxx"  # Optional, increases API rate limit from 60/hr to 5000/hr

# Run the bot
cd src
python bot.py
```

### Testing Changes

There is no formal test suite. To verify changes:

1. Run the bot locally with environment variables configured
2. Check console output for errors
3. Verify Feishu receives the test message
4. Check that `report_YYYYMMDD.md` is generated in `src/`

## Architecture

### Core Components

**`src/bot.py`** - Single-file application containing:

- `GitHubTrendingBot` class with the following key methods:
  - `fetch_trending_repos()` - Main data fetcher using GitHub Search API
  - `fetch_trending_from_web()` - Fallback scraper for GitHub Trending page
  - `generate_report()` - Creates Markdown formatted report
  - `send_to_feishu()` - Sends interactive card messages via Feishu webhook
  - `load_pushed_history()` / `save_pushed_history()` - Manages 90-day deduplication

### Data Flow

1. **Search**: Queries GitHub Search API with 10 AI-related keywords (AI, LLM, MCP, RAG, etc.), filtering for repos updated in last 90 days
2. **Deduplication**: Filters out repos pushed within last 90 days (tracked in `.pushed_history.json`)
3. **Ranking**: Sorts by star velocity (stars per day) rather than total stars
4. **Fallback**: If insufficient results after deduplication, clears history and retries; if still failing, falls back to web scraping
5. **Output**: Saves Markdown report locally and sends card message to Feishu

### Configuration Points

**Environment Variables** (defined in `.env.example`):
- `FEISHU_WEBHOOK` - Required. Feishu bot webhook URL
- `GIT_TOKEN` - Optional. GitHub personal access token with `public_repo` scope

**Modifiable Constants** (in `src/bot.py`):
- `queries` list (line ~80) - Search keywords for GitHub API
- `per_page` parameter - Results per keyword (default: 10)
- `return unique_repos[:5]` - Number of repos to push (default: 5)
- `history_days` - Deduplication window (default: 90 days)

### GitHub Actions Workflow

**`.github/workflows/daily-bot.yml`**:
- Runs on schedule: `0 0 * * *` (UTC 00:00 = Beijing 08:00)
- Can be triggered manually via `workflow_dispatch`
- Python 3.11 runtime
- Uploads daily reports as artifacts (30-day retention)

### Key Files

| File | Purpose |
|------|---------|
| `src/bot.py` | Main application logic |
| `.github/workflows/daily-bot.yml` | CI/CD schedule configuration |
| `requirements.txt` | Python dependencies (only `requests`) |
| `.env.example` | Environment variable template |
| `.pushed_history.json` | Runtime-generated deduplication database |
| `src/report_*.md` | Runtime-generated daily reports |

## Notes

- The bot maintains a 90-day push history to avoid duplicate notifications
- Star velocity (stars/day since creation) is the primary ranking metric
- If fewer than 5 unique repos remain after deduplication, history is cleared and fetch is retried
- The Feishu integration uses interactive card messages with orange theme
