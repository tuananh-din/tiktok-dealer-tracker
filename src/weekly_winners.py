#!/usr/bin/env python3
"""Weekly award winners — a FROZEN honor roll rendered on the public report.

Awards are announced to dealers, so they must NOT silently change if later
crawls shift past-week counts. That is why winners are recorded here by hand
(not recomputed each build). To add a new week, prepend a dict to WEEKLY_WINNERS
with the frozen handle + video-count pairs, ordered best-first.
"""
import csv
import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

# Reward shown on the celebration page for each winner.
PRIZE = "500.000đ + Vinh danh"
WEEK_THRESHOLD = 10                 # số video/tuần tối thiểu để đạt giải

# --- Tuần tự động ---
# Lưới tuần 7 ngày, neo tại ngày bắt đầu Tuần 3 (13/07 – Thứ 2). Từ đó tuần hiện
# tại tự tính theo ngày chạy — team KHÔNG cần sửa tay mỗi tuần nữa.
# (Tuần 2 là tuần ngắn 07/07–12/07, đã chốt cứng trong WEEKLY_WINNERS bên dưới.)
_WEEK_ANCHOR = date(2026, 7, 13)    # Thứ 2, bắt đầu "Tuần 3"
_WEEK_ANCHOR_NUM = 3
_FROZEN_WINNERS_FILE = Path(__file__).resolve().parent.parent / "output" / "weekly-winners.json"


def get_current_week(today=None):
    """Trả về dict tuần đang diễn ra {label,start,end,range,threshold,prize}."""
    if today is None:
        today = date.today()
    elif isinstance(today, str):
        y, m, d = (int(x) for x in today[:10].split("-"))
        today = date(y, m, d)
    idx = (today - _WEEK_ANCHOR).days // 7          # số tuần lệch so với neo
    start = _WEEK_ANCHOR + timedelta(days=idx * 7)
    end = start + timedelta(days=6)
    return {
        "label": f"Tuần {_WEEK_ANCHOR_NUM + idx}",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "range": f"{start:%d/%m} – {end:%d/%m/%Y}",
        "threshold": WEEK_THRESHOLD,
        "prize": PRIZE,
    }

WEEKLY_WINNERS = [
    {
        "week": "Tuần 4",
        "range": "20/07 – 26/07/2026",
        "criteria": "≥ 10 video “qrevo 2 pro” trong tuần",
        # Frozen snapshot 27/07/2026 từ dataset đã đồng bộ trên GitHub.
        "dealers": [
            ("phanthulan715", 15),
            ("3t.smart.robot.tn", 13),
            (".hng0863", 11),
        ],
    },
    {
        "week": "Tuần 3",
        "range": "13/07 – 19/07/2026",
        "criteria": "≥ 10 video “qrevo 2 pro” trong tuần",
        # (handle, số video trong tuần) — best first. Frozen snapshot 20/07/2026.
        # Tối đa 6 đại lý. Đồng hạng ở mốc 10 video: xếp theo ai ĐẠT MỐC 10 SỚM HƠN
        # (kimanh_1202 đạt 17/07 → trên xiaomi.phu.tho 18/07).
        # thietbibepan cũng đủ 10 nhưng đạt mốc muộn nhất (19/07) → KHÔNG tính (chốt 6).
        "dealers": [
            ("phanthulan715", 22),
            ("momimart.vn", 14),
            ("thurobot88", 13),
            (".hng0863", 12),
            ("kimanh_1202", 10),
            ("xiaomi.phu.tho", 10),
        ],
    },
    {
        "week": "Tuần 2",
        "range": "07/07 – 12/07/2026",
        "criteria": "≥ 10 video “qrevo 2 pro” trong tuần",
        # (handle, số video trong tuần) — best first. Frozen snapshot.
        # Đồng hạng ở mốc 10 video: xếp theo ai ĐẠT MỐC 10 SỚM HƠN
        # (xiaomi.phu.tho đạt 10 sớm nhất — 11/07 → hạng 3, huy chương đồng).
        # bothome_robotgialai hoàn thành muộn nhất → KHÔNG tính vào danh sách.
        "dealers": [
            ("phanthulan715", 21),
            ("nc.nh.qu.robot", 16),
            ("xiaomi.phu.tho", 10),
            ("momimart.vn", 10),
            ("thietbibepan", 10),
            ("thurobot88", 10),
        ],
    },
    {
        "week": "Tuần 1",
        "range": "29/06 – 06/07/2026",
        "criteria": "≥ 10 video “qrevo 2 pro” trong tuần",
        # (handle, số video trong tuần) — best first. Frozen snapshot.
        "dealers": [
            ("kimanh_1202", 13),
            ("thurobot88", 13),
            ("phanthulan715", 13),
            ("homecaredigital", 11),
            ("momimart.vn", 11),
            ("thietbibepan", 10),
        ],
    },
]


def get_weekly_winners(path=None) -> list:
    """Return the persisted honor roll, falling back to the seed history.

    The JSON snapshot is committed by GitHub Actions. This makes an announced
    result immutable even after a later metrics refresh, without having to edit
    Python source by hand each week.
    """
    path = Path(path) if path else _FROZEN_WINNERS_FILE
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list) and all(isinstance(w, dict) for w in data):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return deepcopy(WEEKLY_WINNERS)


def _week_for_number(number: int) -> dict:
    start = _WEEK_ANCHOR + timedelta(days=(number - _WEEK_ANCHOR_NUM) * 7)
    end = start + timedelta(days=6)
    return {
        "week": f"Tuần {number}",
        "start": start,
        "end": end,
        "range": f"{start:%d/%m} – {end:%d/%m/%Y}",
        "criteria": "≥ 10 video “qrevo 2 pro” trong tuần",
    }


def freeze_completed_weeks(csv_path, today=None, path=None, max_winners=6) -> list:
    """Freeze every missing completed week when data is available.

    Called after each successful crawl. If GitHub Actions misses Monday, a later
    daily run retries the same unrecorded week instead of silently skipping it.
    """
    if today is None:
        today = date.today()
    elif isinstance(today, str):
        today = date.fromisoformat(today[:10])

    path = Path(path) if path else _FROZEN_WINNERS_FILE
    winners = get_weekly_winners(path)
    known = {w.get("week") for w in winners}
    current_number = int(get_current_week(today)["label"].split()[-1])

    try:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        return []

    added = []
    for number in range(_WEEK_ANCHOR_NUM, current_number):
        wk = _week_for_number(number)
        if wk["week"] in known:
            continue
        start, end = wk["start"].isoformat(), wk["end"].isoformat()
        grouped = {}
        for row in rows:
            uploaded = (row.get("Upload Date") or "")[:10]
            if not (start <= uploaded <= end):
                continue
            handle = (row.get("Channel") or "").strip().lstrip("@").lower()
            if handle:
                grouped.setdefault(handle, []).append(uploaded)

        # Do not publish an empty week after a failed/blocked crawl; retry on
        # the next daily run once video records are available.
        if not grouped:
            continue

        ranked = []
        for handle, uploads in grouped.items():
            uploads.sort()
            if len(uploads) >= WEEK_THRESHOLD:
                # Ties at the threshold go to the dealer that reached it first.
                ranked.append((handle, len(uploads), uploads[WEEK_THRESHOLD - 1]))
        ranked.sort(key=lambda item: (-item[1], item[2], item[0]))
        winners.insert(0, {
            "week": wk["week"],
            "range": wk["range"],
            "criteria": wk["criteria"],
            "dealers": [(handle, count) for handle, count, _ in ranked[:max_winners]],
        })
        known.add(wk["week"])
        added.append(wk["week"])

    # Create the snapshot on the first successful run too, so all later runs
    # read one stable, versioned source of truth.
    if added or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(winners, ensure_ascii=False, indent=2), encoding="utf-8")
    return added
