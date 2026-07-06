#!/usr/bin/env python3
"""Cross-reference the dealer registration sheet against the crawled videos to
find dealers who signed up but have NO 'qrevo 2 pro' video yet.

Feeds the public HTML report's "đại lý chưa có video" section. Only exposes
PUBLIC-safe fields (store name, province, TikTok handle) — never the person's
name or phone from the private form.

Pure standard library + project modules; safe on GitHub Actions (reads the same
public Google Sheet the crawler already uses). Any failure returns None so the
report still builds without this section.
"""
import csv
import re
from pathlib import Path

import config
from src import channel_normalizer as cn


def _handle(raw: str):
    """Raw link/handle -> bare lowercase handle (e.g. 'clickbuy.vn') or None."""
    c = cn.normalize(raw)
    if not c:
        return None
    m = re.search(r"@([A-Za-z0-9._-]+)", c)
    return m.group(1).lower() if m else None


def _find_col(header: list, *keys: str):
    """Index of the first header cell containing any key (case-insensitive)."""
    for i, h in enumerate(header):
        low = h.lower()
        if any(k in low for k in keys):
            return i
    return None


def _video_handles(csv_path: Path) -> set:
    """Set of bare lowercase handles that already have >=1 matching video."""
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return set()
    ch_col = next((c for c in rows[0].keys() if "channel" in c.lower()), None)
    out = set()
    for r in rows:
        v = (r.get(ch_col) or "").strip().lower().lstrip("@")
        if v:
            out.add(v)
    return out


def compute(csv_path):
    """Return a summary dict, or None if the registration sheet is unreachable.

    {
      'no_video': [{'store', 'prov', 'handles': [...]}...],  # has channel, no video
      'n_registered': int, 'n_have': int, 'n_no_channel': int,
    }
    """
    from src import sheet_reader
    try:
        rows = sheet_reader._fetch_rows()
    except Exception:  # noqa: BLE001 - section is optional; never break the report
        return None
    if not rows or len(rows) < 2:
        return None

    header = [h.strip() for h in rows[0]]
    c_store = _find_col(header, "cửa hàng", "đại lý", "dai ly")
    c_prov = _find_col(header, "tỉnh", "thành phố", "tinh")
    keys = [k.lower() for k in config.GSHEET_LINK_COLUMN_KEYS]
    link_cols = [i for i, h in enumerate(header) if any(k in h.lower() for k in keys)]

    have = _video_handles(Path(csv_path))
    no_video, n_have, n_no_channel = [], 0, 0
    for r in rows[1:]:
        def g(i):
            return r[i].strip() if i is not None and i < len(r) else ""

        raws = [g(i) for i in link_cols if g(i)]
        handles = []
        for raw in raws:
            h = _handle(raw)
            if h and h not in handles:
                handles.append(h)
        if not handles:
            n_no_channel += 1
            continue
        if any(h in have for h in handles):
            n_have += 1
            continue
        no_video.append({"store": g(c_store), "prov": g(c_prov), "handles": handles})

    return {
        "no_video": no_video,
        "n_registered": len(rows) - 1,
        "n_have": n_have,
        "n_no_channel": n_no_channel,
    }
