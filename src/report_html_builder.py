#!/usr/bin/env python3
"""Build the public HTML report (index.html) from the full crawled dataset.

Reads output/qrevo-videos.csv, recomputes every metric, and renders a
self-contained light-theme analysis page. Called at the end of each crawl so
the public GitHub Pages report auto-refreshes with the latest data.

Pure standard library — no extra dependencies, safe to run on GitHub Actions.
"""
import csv
import html
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

# --- caption theme buckets (diacritic-insensitive keyword match) ---
THEMES = {
    "Lau/hút/vệ sinh": ["lau", "hut", "ve sinh", "sach", "bui"],
    "Công nghệ/tính năng": ["cong nghe", "tinh nang", " ai", "cam bien", "tu dong"],
    "Giá/khuyến mãi": ["gia ", "giá", "khuyen mai", "sale", "uu dai", "deal", "gi.a"],
    "Review/trải nghiệm": ["review", "trai nghiem", "danh gia"],
    "Lắp đặt/giao hàng": ["lap dat", "giao tan", "ship", "lap tan"],
    "So sánh sản phẩm": ["so sanh", " vs "],
}


# ------------------------- helpers -------------------------
def _vn(n):
    """12345 -> '12.345' (Vietnamese thousands separator)."""
    return f"{int(round(n)):,}".replace(",", ".")


def _vp(x):
    """3.38 -> '3,38' (comma decimal)."""
    return f"{x:.1f}".replace(".", ",")


def _num(x):
    try:
        return int(str(x).replace(",", "").replace(".", "").strip() or 0)
    except ValueError:
        return 0


def _strip_d(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def _week_label(iso_year, iso_week):
    mon = date.fromisocalendar(iso_year, iso_week, 1)
    sun = date.fromisocalendar(iso_year, iso_week, 7)
    return f"{mon:%d/%m}–{sun:%d/%m}"


# ------------------------- compute -------------------------
def compute(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    if not rows:
        return None
    cols = rows[0].keys()

    def col(name):
        for c in cols:
            if name.lower() in c.lower():
                return c
        return None

    K_ch, K_up = col("Channel"), col("Upload")
    K_vw, K_lk, K_cm = col("View"), col("Like"), col("Comment")
    K_cap, K_url = col("Caption"), col("URL")

    per = defaultdict(lambda: {"v": 0, "view": 0, "like": 0, "cmt": 0})
    weeks = Counter()
    views = []
    low100 = zerocmt = 0
    vids = []
    dates = []
    for r in rows:
        ch = r[K_ch]
        vw, lk, cm = _num(r[K_vw]), _num(r[K_lk]), _num(r[K_cm])
        up = (r[K_up] or "").strip()
        cap = (r[K_cap] or "").replace("\n", " ")
        p = per[ch]
        p["v"] += 1; p["view"] += vw; p["like"] += lk; p["cmt"] += cm
        views.append(vw)
        if vw < 100:
            low100 += 1
        if cm == 0:
            zerocmt += 1
        try:
            y, m, d = (int(x) for x in up.split("-"))
            iso = date(y, m, d).isocalendar()
            weeks[(iso[0], iso[1])] += 1
            dates.append(up)
        except (ValueError, TypeError):
            pass
        vids.append({"ch": ch, "view": vw, "like": lk, "cmt": cm,
                     "cap": cap, "url": r[K_url]})

    dealers = []
    for ch, p in per.items():
        eng = (p["like"] + p["cmt"]) / p["view"] * 100 if p["view"] else 0
        dealers.append({"ch": ch, "v": p["v"], "view": p["view"],
                        "like": p["like"], "cmt": p["cmt"], "eng": eng,
                        "avg": p["view"] / p["v"] if p["v"] else 0})
    dealers.sort(key=lambda d: d["view"], reverse=True)

    tot_v = len(rows)
    tot_view = sum(d["view"] for d in dealers)
    tot_like = sum(d["like"] for d in dealers)
    tot_cmt = sum(d["cmt"] for d in dealers)
    views_sorted = sorted(views)
    median = views_sorted[len(views_sorted) // 2] if views_sorted else 0

    reach = dealers[0]
    volume = max(dealers, key=lambda d: d["v"])
    engable = [d for d in dealers if d["view"] >= 150 and d["v"] >= 2]
    engage = max(engable or dealers, key=lambda d: d["eng"])
    weak = {d["ch"] for d in dealers if d["avg"] < 30}

    top3_view = sum(d["view"] for d in dealers[:3])
    top3_v = sum(d["v"] for d in sorted(dealers, key=lambda d: d["v"], reverse=True)[:3])
    dealers_le2 = sum(1 for d in dealers if d["v"] <= 2)

    themes = {}
    for name, kws in THEMES.items():
        c = sum(1 for v in vids if any(k in _strip_d(v["cap"]) for k in kws))
        themes[name] = c

    weeks_sorted = sorted(weeks.items())[-6:]  # last up to 6 weeks
    last_week_ct = weeks_sorted[-1][1] if weeks_sorted else 0

    top_videos = sorted(vids, key=lambda v: v["view"], reverse=True)[:8]

    return {
        "tot_v": tot_v, "n_dealers": len(dealers), "tot_view": tot_view,
        "tot_like": tot_like, "tot_cmt": tot_cmt,
        "eng": (tot_like + tot_cmt) / tot_view * 100 if tot_view else 0,
        "avg_view": tot_view / tot_v if tot_v else 0, "median": median,
        "low100": low100, "low100_pct": round(low100 / tot_v * 100),
        "zerocmt": zerocmt, "zerocmt_pct": round(zerocmt / tot_v * 100),
        "dealers_le2": dealers_le2,
        "top3_view": top3_view,
        "top3_view_pct": round(top3_view / tot_view * 100) if tot_view else 0,
        "top1_view_pct": round(reach["view"] / tot_view * 100) if tot_view else 0,
        "top3_v_pct": round(top3_v / tot_v * 100) if tot_v else 0,
        "weeks": weeks_sorted, "last_week_ct": last_week_ct,
        "last_week_pct": round(last_week_ct / tot_v * 100) if tot_v else 0,
        "themes": themes, "dealers": dealers,
        "reach": reach, "volume": volume, "engage": engage, "weak": weak,
        "top_videos": top_videos,
        "n_weeks": len(weeks),
        "date_min": min(dates) if dates else "", "date_max": max(dates) if dates else "",
    }


# ------------------------- render sections -------------------------
def _f_date(iso):  # '2026-06-08' -> '08/06'
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}"
    except ValueError:
        return iso


def _weekly_bars(s):
    mx = max((c for _, c in s["weeks"]), default=1)
    out = []
    for i, ((yy, ww), c) in enumerate(s["weeks"], 1):
        w = round(c / mx * 100, 1)
        out.append(
            f'<div class="bar-row"><span class="nm">T{i} · {_week_label(yy, ww)}</span>'
            f'<span class="bar-track"><span class="bar-fill g" style="width:{w}%"></span></span>'
            f'<span class="vv">{c} <small>video</small></span></div>')
    return "\n".join(out)


def _concentration_bars(s):
    rest = 100 - s["top3_view_pct"]
    return "\n".join([
        f'<div class="bar-row"><span class="nm">{s["reach"]["ch"]}</span>'
        f'<span class="bar-track"><span class="bar-fill" style="width:{s["top1_view_pct"]}%"></span></span>'
        f'<span class="vv">{s["top1_view_pct"]}% <small>view</small></span></div>',
        f'<div class="bar-row"><span class="nm">Top 3 đại lý</span>'
        f'<span class="bar-track"><span class="bar-fill" style="width:{s["top3_view_pct"]}%"></span></span>'
        f'<span class="vv">{s["top3_view_pct"]}% <small>view</small></span></div>',
        f'<div class="bar-row"><span class="nm">{s["n_dealers"]-3} đại lý còn lại</span>'
        f'<span class="bar-track"><span class="bar-fill a" style="width:{rest}%"></span></span>'
        f'<span class="vv">{rest}% <small>view</small></span></div>',
    ])


def _leaderboard(s):
    out = []
    for i, d in enumerate(s["dealers"], 1):
        tag = ""
        if d["ch"] == s["reach"]["ch"]:
            tag = '<span class="tag reach">REACH</span>'
        elif d["ch"] == s["volume"]["ch"]:
            tag = '<span class="tag vol">VOLUME</span>'
        elif d["ch"] == s["engage"]["ch"]:
            tag = '<span class="tag eng">ENGAGE</span>'
        elif d["ch"] in s["weak"]:
            tag = '<span class="tag weak">YẾU</span>'
        noise = d["view"] < 60
        eng_txt = _vp(d["eng"]) + ("*" if noise else "")
        cls = ""
        if not noise and d["eng"] >= 6:
            cls = "eg-hi"
        elif not noise and d["eng"] < 1.5:
            cls = "eg-lo"
        avg = f'<b>{_vn(d["avg"])}</b>' if d["ch"] == s["reach"]["ch"] else _vn(d["avg"])
        out.append(
            f'<tr><td class="rk">{i}</td><td>{d["ch"]}{tag}</td>'
            f'<td>{d["v"]}</td><td>{_vn(d["view"])}</td><td>{avg}</td>'
            f'<td>{_vn(d["like"])}</td><td>{_vn(d["cmt"])}</td>'
            f'<td class="{cls}">{eng_txt}</td></tr>')
    return "\n".join(out)


def _themes_bars(s):
    items = sorted(s["themes"].items(), key=lambda kv: kv[1], reverse=True)
    out = []
    for name, c in items:
        pct = round(c / s["tot_v"] * 100)
        fill = "" if pct >= 20 else "a"
        out.append(
            f'<div class="bar-row"><span class="nm">{name}</span>'
            f'<span class="bar-track"><span class="bar-fill {fill}" style="width:{max(pct,1)}%"></span></span>'
            f'<span class="vv">{pct}% <small>· {c}</small></span></div>')
    return "\n".join(out)


def _top_videos(s):
    out = []
    for i, v in enumerate(s["top_videos"], 1):
        cap = v["cap"][:66].strip()
        out.append(
            f'<div class="vrow"><div class="vn">{i}</div>'
            f'<div class="vc"><div class="cap"><a href="{v["url"]}" target="_blank" rel="noopener">{cap}</a></div>'
            f'<div class="ch">{v["ch"]}</div></div>'
            f'<div class="vm"><b>{_vn(v["view"])}</b> view<br>{_vn(v["like"])} tym · {_vn(v["cmt"])} cmt</div></div>')
    return "\n".join(out)


def _pending_section(p):
    """Registered-but-no-video dealers. Empty string if none / sheet unavailable."""
    if not p or not p.get("no_video"):
        return ""
    rows = []
    for i, d in enumerate(p["no_video"], 1):
        chips = "".join(
            f'<a href="https://www.tiktok.com/@{h}" target="_blank" rel="noopener">@{h}</a>'
            for h in d["handles"])
        store = html.escape(d["store"]) or "—"
        prov = html.escape(d["prov"]) or "—"
        rows.append(
            f'<tr><td class="rk">{i}</td><td>{store}</td>'
            f'<td>{prov}</td><td class="ch">{chips}</td></tr>')
    n_nov = len(p["no_video"])
    return (
        '\n  <h2 class="sec"><span class="bar"></span>Đại lý đã đăng ký nhưng chưa có video</h2>'
        f'\n  <p class="sec-note">{p["n_registered"]} đại lý đăng ký · {p["n_have"]} đã có video · '
        f'<b>{n_nov} kênh chưa xuất hiện video “qrevo 2 pro”</b> '
        '(chưa thấy trong ~30 video gần nhất) — danh sách để nhắc & kích hoạt.</p>'
        '\n  <div class="tbl-wrap"><table class="pend">'
        '<thead><tr><th>#</th><th>Cửa hàng / Đại lý</th><th>Tỉnh/TP</th>'
        '<th>Kênh TikTok</th></tr></thead><tbody>\n'
        + "\n".join(rows)
        + '\n</tbody></table></div>\n'
    )


def _theme_pct(s, name):
    return round(s["themes"].get(name, 0) / s["tot_v"] * 100)


def _recos(s):
    price = _theme_pct(s, "Giá/khuyến mãi")
    comp = _theme_pct(s, "So sánh sản phẩm")
    r, e = s["reach"], s["engage"]
    items = [
        ("p1", f"Bóc “công thức {r['ch']}” thành brief mẫu cho toàn hệ thống",
         f"Kênh này giữ top video với {_vn(r['avg'])} view/video (gấp {r['avg']/s['avg_view']:.1f}× TB). "
         f"Chuẩn hoá format thắng (kịch bản + hashtag) rồi gửi cho {s['n_dealers']-1} đại lý còn lại — "
         f"đòn bẩy nhanh & rẻ nhất."),
        ("p1", "Bổ sung tầng nội dung “chốt sale”",
         f"Chỉ {price}% video nhắc giá/khuyến mãi, {comp}% so sánh. Yêu cầu mỗi đại lý tối thiểu "
         f"<b>1 video giá + 1 video so sánh</b> mỗi tháng, kèm <b>CTA + hotline/link</b> trong caption "
         f"để biến view thành lead."),
        ("p2", "Kích hoạt lại nhóm đại lý “đăng rồi dừng”",
         f"{s['dealers_le2']}/{s['n_dealers']} đại lý mới đăng ≤2 video; {s['low100_pct']}% video &lt;100 view. "
         f"Đặt <b>KPI tối thiểu 4 video/tháng</b> + thưởng theo view/tương tác, nhắc riêng các kênh gần như “chết”."),
        ("p2", f"Nhân rộng cách tạo tương tác của {e['ch']}",
         f"Đạt {_vp(e['eng'])}% eng khi {s['zerocmt_pct']}% video toàn hệ thống có 0 bình luận. "
         f"Mời chia sẻ cách đặt câu hỏi/CTA khơi hội thoại; áp dụng cho cả kênh reach cao nhưng eng thấp."),
        ("p3", "Giữ đà tuần cuối & theo dõi giữ nhịp",
         f"Tuần gần nhất có {s['last_week_ct']} video ({s['last_week_pct']}% kỳ). Theo dõi tuần kế tiếp có "
         f"giữ nhịp không hay chỉ là đợt phát động. Trang này cập nhật hằng ngày để phát hiện sớm nếu tụt."),
    ]
    out = []
    for pri, h, body in items:
        out.append(
            f'<div class="reco"><div class="pri {pri}">{pri.upper()}</div>'
            f'<div class="rc"><h4>{h}</h4><p>{body}</p></div></div>')
    return "\n".join(out)


# ------------------------- render page -------------------------
def render(s, snapshot, pending=None):
    price = _theme_pct(s, "Giá/khuyến mãi")
    comp = _theme_pct(s, "So sánh sản phẩm")
    period = f"{_f_date(s['date_min'])} – {_f_date(s['date_max'])}/{s['date_max'][:4]}"
    return _TEMPLATE.format(
        css=_CSS,
        pending_section=_pending_section(pending),
        period=period, snapshot=snapshot,
        n_dealers=s["n_dealers"], tot_v=s["tot_v"], n_weeks=s["n_weeks"],
        tot_view=_vn(s["tot_view"]), avg=_vn(s["avg_view"]), median=_vn(s["median"]),
        tot_like=_vn(s["tot_like"]), tot_cmt=_vn(s["tot_cmt"]), eng=_vp(s["eng"]),
        last_ct=s["last_week_ct"], last_pct=s["last_week_pct"],
        top3_view_pct=s["top3_view_pct"], top1_view_pct=s["top1_view_pct"],
        reach_ch=s["reach"]["ch"], reach_avg=_vn(s["reach"]["avg"]),
        reach_mult=f"{s['reach']['avg']/s['avg_view']:.1f}".replace(".", ","),
        reach_view_pct=s["top1_view_pct"], reach_eng=_vp(s["reach"]["eng"]),
        vol_ch=s["volume"]["ch"], vol_v=s["volume"]["v"], vol_avg=_vn(s["volume"]["avg"]),
        vol_eng=_vp(s["volume"]["eng"]),
        eng_ch=s["engage"]["ch"], eng_val=_vp(s["engage"]["eng"]),
        eng_like=_vn(s["engage"]["like"]), eng_cmt=_vn(s["engage"]["cmt"]),
        eng_view=_vn(s["engage"]["view"]), eng_v=s["engage"]["v"],
        low100_pct=s["low100_pct"], low100=s["low100"],
        zerocmt_pct=s["zerocmt_pct"], zerocmt=s["zerocmt"],
        dealers_le2=s["dealers_le2"],
        price=price, comp=comp,
        weekly_bars=_weekly_bars(s), conc_bars=_concentration_bars(s),
        leaderboard=_leaderboard(s), themes_bars=_themes_bars(s),
        top_videos=_top_videos(s), recos=_recos(s),
    )


def build(csv_path, out_paths, snapshot=None):
    """Compute + render + write. out_paths: str/Path or list of them."""
    snapshot = snapshot or f"{datetime.now():%d/%m/%Y}"
    s = compute(Path(csv_path))
    if not s:
        return None
    try:  # optional: registered-but-no-video list (needs the public reg sheet)
        from src import pending_dealers
        pending = pending_dealers.compute(Path(csv_path))
    except Exception:  # noqa: BLE001 - never let this section break the report
        pending = None
    page = render(s, snapshot, pending)
    if isinstance(out_paths, (str, Path)):
        out_paths = [out_paths]
    for p in out_paths:
        Path(p).write_text(page, encoding="utf-8")
    return s


# CSS + template live in a sibling file to keep this module focused.
from src.report_html_template import CSS as _CSS, TEMPLATE as _TEMPLATE  # noqa: E402


if __name__ == "__main__":
    import config
    st = build(config.CSV_FILE,
               [config.BASE_DIR / "index.html",
                config.BASE_DIR / "bao-cao-qrevo2pro-tiktok.html"])
    print("Built report:", st["tot_v"] if st else 0, "videos")
