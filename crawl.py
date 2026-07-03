#!/usr/bin/env python3
"""Daily crawler: scan dealer TikTok channels, collect videos whose caption
mentions the target keyword(s), and write them to Google Sheets and/or Excel.

Input (channel list) and output (report) default to Google Sheets so it runs
headless on GitHub Actions — no local machine needed.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from src import excel_writer
from src import keyword_filter as kf
from src import tiktok_crawler as crawler


def log(msg: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _read_channels_from_file() -> list:
    if not config.CHANNELS_FILE.exists():
        return []
    out = []
    for ln in config.CHANNELS_FILE.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.append(ln)
    return out


def get_channels() -> list:
    if config.CHANNELS_SOURCE == "google_sheet_public":
        from src import channel_normalizer, sheet_reader
        raw = sheet_reader.read_channel_links()
        channels, bad = channel_normalizer.normalize_many(raw)
        if bad:
            log(f"  (skipped {len(bad)} unparseable links: {bad[:3]}...)")
        return channels
    if config.CHANNELS_SOURCE == "google_sheets":
        from src import sheets_client
        return sheets_client.read_channels()
    return _read_channels_from_file()


def get_existing_urls() -> set:
    """Union of URLs already recorded across all enabled outputs (dedupe)."""
    urls = set()
    if "google_sheets" in config.OUTPUTS:
        from src import sheets_client
        urls |= sheets_client.existing_urls()
    if "excel" in config.OUTPUTS:
        urls |= excel_writer.existing_urls(config.EXCEL_FILE)
    return urls


def write_outputs(rows: list) -> None:
    if "google_sheets" in config.OUTPUTS:
        from src import sheets_client
        n = sheets_client.append_rows(rows)
        log(f"  -> Google Sheets: +{n} rows")
    if "excel" in config.OUTPUTS:
        excel_writer.append_rows(config.EXCEL_FILE, rows)
        excel_writer.export_csv(config.EXCEL_FILE, config.CSV_FILE)
        log(f"  -> Excel: {config.EXCEL_FILE}")


def _fmt_date(yyyymmdd: str) -> str:
    if yyyymmdd and len(yyyymmdd) == 8:
        return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"
    return yyyymmdd or ""


def main() -> None:
    channels = get_channels()
    if not channels:
        log("No channels found (check input source / channels list).")
        return

    patterns = kf.build_patterns(config.KEYWORDS)
    already = get_existing_urls()
    today = f"{datetime.now():%Y-%m-%d}"
    since = config.SINCE_DATE.replace("-", "")  # "YYYYMMDD" floor, or "" for none

    log(f"Start | {len(channels)} channels | keywords={config.KEYWORDS} "
        f"| max={config.MAX_VIDEOS_PER_CHANNEL} since={since or 'all'} "
        f"| {len(already)} already recorded")
    new_matches = []

    for ch in channels:
        try:
            listed = crawler.list_recent_video_ids(ch, config.MAX_VIDEOS_PER_CHANNEL)
        except Exception as e:  # noqa: BLE001 - keep run alive per channel
            log(f"  ! list failed {ch}: {e}")
            continue
        log(f"  {ch}: {len(listed)} recent videos")

        for _vid, vurl, udate in listed:
            if since and udate and udate < since:  # older than floor -> skip (no extract)
                continue
            if vurl in already:            # skip videos already reported
                continue
            try:
                meta = crawler.extract_video(vurl)
            except Exception as e:  # noqa: BLE001
                log(f"    ! extract failed {vurl}: {e}")
                continue
            if not meta:
                continue
            matched = kf.match_keywords(meta["caption"], patterns)
            if not matched or meta["url"] in already:
                continue
            already.add(meta["url"])
            new_matches.append({
                "collected_date": today,
                "channel": meta["uploader"] or ch,
                "keyword": ", ".join(matched),
                "upload_date": _fmt_date(meta["upload_date"]),
                "url": meta["url"],
                "caption": meta["caption"],
                "views": meta["views"],
                "likes": meta["likes"],
                "comments": meta["comments"],
            })
            log(f"    MATCH [{', '.join(matched)}] {meta['url']}")
        time.sleep(config.REQUEST_SLEEP_SECONDS)

    if new_matches:
        write_outputs(new_matches)
    log(f"Done | {len(new_matches)} new matching videos")


if __name__ == "__main__":
    main()
