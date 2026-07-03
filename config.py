"""Central configuration for the TikTok dealer-video tracker."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# =========================================================================
# INPUT — where the dealer channel list comes from
#   "google_sheet_public" : read a PUBLIC (link-viewable) sheet via CSV export
#                           — NO credentials needed. (recommended)
#   "google_sheets"       : read via gspread service account (private sheets)
#   "file"                : read from channels.txt (local fallback)
# =========================================================================
CHANNELS_SOURCE = "google_sheet_public"
CHANNELS_FILE = BASE_DIR / "channels.txt"   # used only when source == "file"

# Public-sheet input: the dealer Google Form responses.
GSHEET_GID = "993548586"                       # the tab's gid (from the URL)
# Pull channel links from every column whose header contains any of these:
GSHEET_LINK_COLUMN_KEYS = ["Link kênh TikTok"]  # matches "đã có" + "mới tạo"

# =========================================================================
# OUTPUT — where the daily report is written (one or both)
#   "google_sheets" : append rows to a Google Sheet tab (recommended)
#   "excel"         : write output/qrevo-videos.xlsx (+ .csv)
# =========================================================================
# Starts logging to the GitHub repo (Excel + CSV). Add "google_sheets" once
# credentials are set:  OUTPUTS = ["excel", "google_sheets"]
OUTPUTS = ["excel"]

# --- Google Sheets settings (input + output live in the SAME spreadsheet) ---
# Get the ID from the sheet URL:
#   https://docs.google.com/spreadsheets/d/<THIS_IS_THE_ID>/edit
# The spreadsheet ID unlocks dealer PII (names/phones/addresses), so it is NEVER
# hardcoded. Read from env (GitHub secret GSHEET_ID) or a local gitignored file
# `sheet-id.txt`. This keeps the public repo free of the dealer sheet link.
def _load_sheet_id() -> str:
    v = os.environ.get("GSHEET_ID", "").strip()
    if v:
        return v
    f = BASE_DIR / "sheet-id.txt"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


GSHEET_ID = _load_sheet_id()
GSHEET_NAME = "Qrevo Dealer Tracker"  # fallback if GSHEET_ID is empty (open by name)
GSHEET_CHANNELS_TAB = "channels"      # input tab: channels in column A (row 1 = header)
GSHEET_CHANNEL_COL = 1                # column A
GSHEET_OUTPUT_TAB = "videos"          # output report tab (auto-created)

# Service-account JSON. In GitHub Actions it's written from the
# GOOGLE_CREDENTIALS secret; locally place the file next to config.py.
GOOGLE_CREDENTIALS_FILE = BASE_DIR / "google-credentials.json"

# --- Keyword matching ---
# Spaces match flexibly: "qrevo 2 pro" == "qrevo2pro" == "qrevo  2 pro".
# Case-insensitive, ignores Vietnamese diacritics.
KEYWORDS = [
    "qrevo 2 pro",
]

# --- Crawl behavior ---
# Both overridable via env for one-off deep backfills, e.g.:
#   MAX_VIDEOS=250 SINCE_DATE=2026-05-01 python crawl.py
MAX_VIDEOS_PER_CHANNEL = int(os.environ.get("MAX_VIDEOS", "30"))  # videos to list per channel
# Only fully-scan videos uploaded on/after this date (cheap flat-list date filter).
# Empty = no floor. Format "YYYY-MM-DD" or "YYYYMMDD".
SINCE_DATE = os.environ.get("SINCE_DATE", "")
REQUEST_SLEEP_SECONDS = 1.5   # polite delay between channels to avoid rate limits

# --- Local Excel output (used only when "excel" in OUTPUTS) ---
OUTPUT_DIR = BASE_DIR / "output"
EXCEL_FILE = OUTPUT_DIR / "qrevo-videos.xlsx"
CSV_FILE = OUTPUT_DIR / "qrevo-videos.csv"

LOG_FILE = BASE_DIR / "run.log"

# --- Cookies (optional, recommended on GitHub Actions) ---
# TikTok often blocks datacenter IPs. Provide a Netscape-format cookies.txt to
# authenticate as a logged-in browser. Used automatically if the file exists.
COOKIES_FILE = BASE_DIR / "cookies.txt"
