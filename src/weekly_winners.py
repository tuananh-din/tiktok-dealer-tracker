#!/usr/bin/env python3
"""Weekly award winners — a FROZEN honor roll rendered on the public report.

Awards are announced to dealers, so they must NOT silently change if later
crawls shift past-week counts. That is why winners are recorded here by hand
(not recomputed each build). To add a new week, prepend a dict to WEEKLY_WINNERS
with the frozen handle + video-count pairs, ordered best-first.
"""

# Reward shown on the celebration page for each winner.
PRIZE = "500.000đ + Vinh danh"

# Tuần ĐANG diễn ra — đại lý đang đua để đạt ngưỡng nhận giải. Cập nhật mỗi tuần
# (đổi label/start/end/range). Trang celebrate dùng để hiện tiến độ + động viên.
CURRENT_WEEK = {
    "label": "Tuần 2",
    "start": "2026-07-07",          # YYYY-MM-DD, tính cả 2 đầu
    "end":   "2026-07-13",
    "range": "07/07 – 13/07/2026",
    "threshold": 10,                # số video tối thiểu để đạt giải
    "prize": "500.000đ + Vinh danh",
}

WEEKLY_WINNERS = [
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
