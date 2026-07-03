#!/usr/bin/env bash
# Daily runner for the TikTok dealer-video tracker (called by launchd/cron at 17:00).
set -euo pipefail

DIR="/Users/Tuananh/tiktok-dealer-tracker"
cd "$DIR"

# Keep yt-dlp fresh — TikTok changes often. Never let this block the run.
"$DIR/.venv/bin/pip" install --quiet --upgrade yt-dlp >/dev/null 2>&1 || true

"$DIR/.venv/bin/python" "$DIR/crawl.py" >> "$DIR/run.log" 2>&1
