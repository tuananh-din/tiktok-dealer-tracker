#!/usr/bin/env python3
"""Weekly award winners — a FROZEN honor roll rendered on the public report.

Awards are announced to dealers, so they must NOT silently change if later
crawls shift past-week counts. That is why winners are recorded here by hand
(not recomputed each build). To add a new week, prepend a dict to WEEKLY_WINNERS
with the frozen handle + video-count pairs, ordered best-first.
"""
from datetime import date, timedelta

# Reward shown on the celebration page for each winner.
PRIZE = "500.000đ + Vinh danh"
WEEK_THRESHOLD = 10                 # số video/tuần tối thiểu để đạt giải

# --- Tuần tự động ---
# Lưới tuần 7 ngày, neo tại ngày bắt đầu Tuần 2. Từ đó tuần hiện tại tự tính theo
# ngày chạy — team KHÔNG cần sửa tay mỗi tuần nữa.
_WEEK_ANCHOR = date(2026, 7, 7)     # Thứ 2, bắt đầu "Tuần 2"
_WEEK_ANCHOR_NUM = 2


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
        "week": "Tuần 2",
        "range": "07/07 – 13/07/2026",
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
