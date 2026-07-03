"""Read the dealer channel list from a PUBLIC Google Sheet via CSV export.

No credentials needed as long as the sheet is link-viewable ("Anyone with the
link can view"). Only writing to a sheet needs a service account.
"""
import csv
import io
import urllib.request

import config


def _csv_export_url() -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{config.GSHEET_ID}"
        f"/export?format=csv&gid={config.GSHEET_GID}"
    )


def _fetch_rows() -> list:
    req = urllib.request.Request(_csv_export_url(), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8", "replace")
    return list(csv.reader(io.StringIO(data)))


def read_channel_links() -> list:
    """Raw link values from every column whose header matches a configured key."""
    rows = _fetch_rows()
    if not rows:
        return []
    header = [h.strip() for h in rows[0]]
    keys = [k.lower() for k in config.GSHEET_LINK_COLUMN_KEYS]
    col_idx = [i for i, h in enumerate(header) if any(k in h.lower() for k in keys)]
    links = []
    for r in rows[1:]:
        for i in col_idx:
            if i < len(r) and r[i].strip():
                links.append(r[i].strip())
    return links
