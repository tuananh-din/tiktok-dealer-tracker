"""Thin yt-dlp wrappers to list and extract TikTok videos (no API key needed)."""
import json
import shutil
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# Prefer the venv yt-dlp locally; fall back to a PATH yt-dlp (e.g. in CI).
_VENV_YTDLP = _ROOT / ".venv" / "bin" / "yt-dlp"
_YTDLP = str(_VENV_YTDLP) if _VENV_YTDLP.exists() else (shutil.which("yt-dlp") or "yt-dlp")

# Optional Netscape-format cookies to avoid TikTok blocking datacenter IPs.
_COOKIES = _ROOT / "cookies.txt"


def _cookie_args() -> list:
    return ["--cookies", str(_COOKIES)] if _COOKIES.exists() else []


def normalize_channel_url(handle: str) -> str:
    """Accept '@handle', 'handle', or a full URL -> canonical channel URL."""
    handle = handle.strip()
    if handle.startswith("http"):
        return handle.rstrip("/")
    if not handle.startswith("@"):
        handle = "@" + handle
    return f"https://www.tiktok.com/{handle}"


def _iter_json_lines(stdout: str):
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def list_recent_video_ids(handle: str, max_items: int) -> list:
    """Fast flat listing -> list of (video_id, video_url, upload_date), newest first.

    upload_date is 'YYYYMMDD' (or '' if TikTok omitted it) and lets the caller
    date-filter cheaply before doing the expensive per-video full extraction.
    """
    channel_url = normalize_channel_url(handle)
    cmd = [
        _YTDLP, "--flat-playlist", "--dump-json", "--no-warnings",
        "--ignore-errors", "--socket-timeout", "30",
        *_cookie_args(),
        "--playlist-items", f"1-{max_items}", channel_url,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    results = []
    for d in _iter_json_lines(out.stdout):
        vid = d.get("id")
        if not vid:
            continue
        vurl = d.get("webpage_url") or d.get("url") or f"{channel_url}/video/{vid}"
        results.append((vid, vurl, d.get("upload_date") or ""))
    return results


def extract_video(video_url: str) -> dict | None:
    """Full extraction of a single video -> flattened metadata dict."""
    cmd = [
        _YTDLP, "--dump-json", "--no-warnings", "--ignore-errors",
        "--socket-timeout", "30", *_cookie_args(), video_url,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    for d in _iter_json_lines(out.stdout):
        return {
            "id": d.get("id"),
            "url": d.get("webpage_url") or video_url,
            "caption": d.get("description") or d.get("title") or "",
            "upload_date": d.get("upload_date") or "",
            "timestamp": d.get("timestamp"),
            "uploader": d.get("uploader") or d.get("channel") or "",
            "views": d.get("view_count"),
            "likes": d.get("like_count"),
            "comments": d.get("comment_count"),
        }
    return None
