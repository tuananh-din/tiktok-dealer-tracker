#!/usr/bin/env python3
"""Team-facing list of personalized celebration links — one per registered
dealer — so the team can blast them via Zalo. Each dealer opens their own
progress page without typing their handle.

Reads the registration sheet (store + handle), joins current-week video count,
writes output/dealer-links.csv:
    Cửa hàng | Tỉnh/TP | Handle | Video tuần này | Link vinh danh
Sorted by this-week videos (đang dẫn đầu lên trước). Public handles/links only.
"""
import csv
import re
from pathlib import Path

import config
from src import channel_normalizer as cn
from src import dealer_progress

# Trang celebrate công khai trên GitHub Pages.
BASE_LINK = ("https://tuananh-din.github.io/tiktok-dealer-tracker/"
             "celebrate.html?dealer=")


def _handle(raw: str):
    c = cn.normalize(raw)
    if not c:
        return None
    m = re.search(r"@([A-Za-z0-9._-]+)", c)
    return m.group(1).lower() if m else None


def _find_col(header, *keys):
    for i, h in enumerate(header):
        if any(k in h.lower() for k in keys):
            return i
    return None


def write_csv(csv_path, out_path) -> int:
    from src import sheet_reader
    try:
        rows = sheet_reader._fetch_rows()
    except Exception:  # noqa: BLE001 - optional
        return 0
    if not rows or len(rows) < 2:
        return 0

    header = [h.strip() for h in rows[0]]
    c_store = _find_col(header, "cửa hàng", "đại lý", "dai ly")
    c_prov = _find_col(header, "tỉnh", "thành phố", "tinh")
    keys = [k.lower() for k in config.GSHEET_LINK_COLUMN_KEYS]
    link_cols = [i for i, h in enumerate(header) if any(k in h.lower() for k in keys)]

    dealers = dealer_progress.build(Path(csv_path))["dealers"]
    seen, out = set(), []
    for r in rows[1:]:
        def g(i):
            return r[i].strip() if i is not None and i < len(r) else ""

        handles = []
        for i in link_cols:
            h = _handle(g(i))
            if h and h not in handles:
                handles.append(h)
        for h in handles:
            if h in seen:
                continue
            seen.add(h)
            wk = dealers.get(h, {}).get("week_videos", 0)
            out.append([g(c_store), g(c_prov), "@" + h, wk, BASE_LINK + h])

    out.sort(key=lambda x: (-x[3], (x[0] or "").lower()))
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Cửa hàng", "Tỉnh/TP", "Handle", "Video tuần này", "Link vinh danh"])
        w.writerows(out)
    return len(out)


if __name__ == "__main__":
    n = write_csv(config.CSV_FILE, config.OUTPUT_DIR / "dealer-links.csv")
    print(f"Wrote dealer-links.csv: {n} dealers")
