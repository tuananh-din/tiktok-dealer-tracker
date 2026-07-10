#!/usr/bin/env python3
"""Per-dealer progress for the CURRENT (in-progress) week.

Powers the celebration page's live "tuần này bạn đã đăng X/10 video" motivation
for EVERY dealer — winner or not. Reads the crawled video CSV, counts each
handle's videos within CURRENT_WEEK, and writes output/dealer-progress.json.

Public-safe only (TikTok handle + video counts) — never PII. Runs each crawl so
GitHub Actions commits an up-to-date file (lives under output/).
"""
import csv
import json
from pathlib import Path

from src.weekly_winners import get_current_week


def _ymd(s: str) -> str:
    return (s or "").replace("-", "").strip()


def build(csv_path, today=None):
    wk = get_current_week(today)
    lo, hi = _ymd(wk["start"]), _ymd(wk["end"])
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    ch_col = up_col = None
    if rows:
        cols = rows[0].keys()
        ch_col = next((c for c in cols if "channel" in c.lower()), None)
        up_col = next((c for c in cols if "upload" in c.lower()), None)

    week, total = {}, {}
    for r in rows:
        h = (r.get(ch_col) or "").strip().lower().lstrip("@")
        if not h:
            continue
        total[h] = total.get(h, 0) + 1
        up = _ymd((r.get(up_col) or "")[:10])
        if lo <= up <= hi:
            week[h] = week.get(h, 0) + 1

    dealers = {h: {"week_videos": week.get(h, 0), "total_videos": total[h]}
               for h in total}
    return {
        "week": wk["label"],
        "range": wk["range"],
        "start": wk["start"],
        "end": wk["end"],
        "threshold": wk["threshold"],
        "prize": wk["prize"],
        "dealers": dealers,
    }


def write_json(csv_path, out_path) -> int:
    data = build(Path(csv_path))
    Path(out_path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data["dealers"])


if __name__ == "__main__":
    import config
    n = write_json(config.CSV_FILE, config.OUTPUT_DIR / "dealer-progress.json")
    print(f"Wrote dealer-progress.json: {n} dealers")
