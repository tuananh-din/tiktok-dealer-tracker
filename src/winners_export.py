#!/usr/bin/env python3
"""Export the frozen weekly award winners to output/winners.json.

The public celebration page (celebrate.html) fetches this file to decide who is
a winner and what to show. Flat-array shape (one object per winner) so the page
can simply .find() by handle:

    [
      {"week","range","criteria","handle","videos","rank","medal","prize"},
      ...
    ]

Only PUBLIC-safe fields (handle, counts, rank) — never PII. Runs each crawl so
GitHub Actions commits an up-to-date winners.json (it lives under output/).
"""
import json
from pathlib import Path

from src.weekly_winners import PRIZE, WEEKLY_WINNERS

_MEDALS = {1: "gold", 2: "silver", 3: "bronze"}


def build_records() -> list:
    """Flatten WEEKLY_WINNERS into the celebrate.html record shape."""
    records = []
    for wk in WEEKLY_WINNERS:
        for i, (handle, videos) in enumerate(wk["dealers"]):
            rank = i + 1
            records.append({
                "week": wk["week"],
                "range": wk["range"],
                "criteria": wk["criteria"],
                "handle": handle,
                "videos": videos,
                "rank": rank,
                "medal": _MEDALS.get(rank, ""),
                "prize": PRIZE,
            })
    return records


def write_json(path) -> int:
    """Write winners.json; return number of winner records written."""
    records = build_records()
    Path(path).write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(records)


if __name__ == "__main__":
    import config
    n = write_json(config.OUTPUT_DIR / "winners.json")
    print(f"Wrote winners.json: {n} winner records")
