"""Google Sheets I/O: read the dealer channel list (input) and read/append the
video report (output). One spreadsheet, two tabs.

Auth: a service-account JSON at config.GOOGLE_CREDENTIALS_FILE. On GitHub Actions
the JSON is written from the GOOGLE_CREDENTIALS secret.
Requires: pip install gspread
"""
import config

HEADERS = [
    "Collected Date", "Channel", "Keyword", "Upload Date",
    "Video URL", "Caption", "Views", "Likes", "Comments",
]
_URL_COL = 5  # 1-based column of "Video URL" in HEADERS

_sh = None  # cached spreadsheet handle within a single run


def _spreadsheet():
    global _sh
    if _sh is not None:
        return _sh
    import gspread
    gc = gspread.service_account(filename=str(config.GOOGLE_CREDENTIALS_FILE))
    _sh = gc.open_by_key(config.GSHEET_ID) if config.GSHEET_ID else gc.open(config.GSHEET_NAME)
    return _sh


def _output_ws():
    import gspread
    sh = _spreadsheet()
    try:
        return sh.worksheet(config.GSHEET_OUTPUT_TAB)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(config.GSHEET_OUTPUT_TAB, rows=2000, cols=len(HEADERS))
        ws.append_row(HEADERS)
        return ws


def read_channels() -> list:
    """Channels from column A of the input tab (skips header + blanks + #comments)."""
    sh = _spreadsheet()
    ws = sh.worksheet(config.GSHEET_CHANNELS_TAB)
    values = ws.col_values(config.GSHEET_CHANNEL_COL)
    out = []
    for i, v in enumerate(values):
        v = (v or "").strip()
        if i == 0 or not v or v.startswith("#"):
            continue
        out.append(v)
    return out


def existing_urls() -> set:
    """Video URLs already in the report tab, for cross-run dedupe."""
    ws = _output_ws()
    return {v for v in ws.col_values(_URL_COL)[1:] if v}  # skip header


def append_rows(rows) -> int:
    """Append matched-video rows to the report tab."""
    if not rows:
        return 0
    ws = _output_ws()
    payload = [
        [
            r.get("collected_date"), r.get("channel"), r.get("keyword"),
            r.get("upload_date"), r.get("url"), r.get("caption"),
            r.get("views"), r.get("likes"), r.get("comments"),
        ]
        for r in rows
    ]
    ws.append_rows(payload, value_input_option="USER_ENTERED")
    return len(payload)
