#!/usr/bin/env python3
"""Weekly award winners — a FROZEN honor roll rendered on the public report.

Awards are announced to dealers, so they must NOT silently change if later
crawls shift past-week counts. That is why winners are recorded here by hand
(not recomputed each build). To add a new week, prepend a dict to WEEKLY_WINNERS
with the frozen handle + video-count pairs, ordered best-first.
"""

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
