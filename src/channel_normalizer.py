"""Normalize messy TikTok links into canonical channel URLs.

Handles: full URLs with tracking params, missing scheme, bare usernames,
bare @handles, video URLs, and vt.tiktok.com / vm.tiktok.com short links.
"""
import re
import urllib.request

_HANDLE_RE = re.compile(r"tiktok\.com/@([A-Za-z0-9._-]+)")
_SHORT_HOSTS = ("vt.tiktok.com", "vm.tiktok.com")


def _resolve_short(url: str) -> str:
    """Follow redirects on a short share link to reach the real URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl()
    except Exception:  # noqa: BLE001 - unreachable link -> leave as-is
        return url


def normalize(raw: str):
    """Return 'https://www.tiktok.com/@handle' or None if unparseable."""
    if not raw:
        return None
    s = raw.strip()

    # No domain -> treat as a bare username or @handle.
    if "tiktok.com" not in s.lower():
        token = s[1:] if s.startswith("@") else s
        token = token.split("?")[0].strip().strip("/")
        if token and " " not in token and "/" not in token:
            return f"https://www.tiktok.com/@{token}"
        return None

    url = s if s.startswith("http") else "https://" + s.lstrip("/")
    if any(h in url.lower() for h in _SHORT_HOSTS):
        url = _resolve_short(url)
    m = _HANDLE_RE.search(url)
    return f"https://www.tiktok.com/@{m.group(1)}" if m else None


def normalize_many(raws):
    """Normalize a list of raw links; dedupe, preserve order. Returns (channels, unparseable)."""
    seen, channels, bad = set(), [], []
    for raw in raws:
        c = normalize(raw)
        if c is None:
            bad.append(raw)
        elif c not in seen:
            seen.add(c)
            channels.append(c)
    return channels, bad
