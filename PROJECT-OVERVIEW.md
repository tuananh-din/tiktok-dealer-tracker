# TikTok Dealer Video Tracker — Project Overview

> Tài liệu mô tả toàn bộ dự án để một LLM (GPT/Claude) hiểu ngữ cảnh trước khi
> hỗ trợ xây tính năng mới (ví dụ: trang web "gift/celebration" bắn pháo hoa
> tung hô đại lý đoạt giải). Viết tính đến 09/07/2026.

---

## 1. Dự án làm gì (elevator pitch)

Một hệ thống **theo dõi tự động** các video TikTok của **đại lý** (dealer) đăng
về sản phẩm robot hút bụi **Qrevo 2 Pro**. Mỗi ngày hệ thống:

1. Đọc danh sách kênh TikTok của đại lý (từ Google Form → Google Sheet công khai).
2. Crawl video gần đây của từng kênh, **lọc video có caption chứa từ khoá
   "qrevo 2 pro"** (không phân biệt hoa/thường, bỏ dấu tiếng Việt).
3. Cào view/like/comment, **refresh lại số liệu** cho video đăng trong 21 ngày
   (vì view tăng dần sau khi đăng).
4. Ghi ra Excel/CSV + **dựng lại một trang dashboard HTML công khai** (GitHub Pages).
5. Commit kết quả thẳng vào repo → dashboard tự cập nhật.

Mục tiêu kinh doanh: chạy **chương trình thi đua** cho đại lý — đại lý đăng nhiều
video chất lượng thì được **vinh danh + thưởng theo tuần**.

---

## 2. Kiến trúc & luồng dữ liệu

```
Google Form (đại lý đăng ký kênh)
        │
        ▼
Google Sheet công khai (CSV export, không cần credentials)
        │  channels
        ▼
┌─────────────────────── crawl.py (điều phối) ───────────────────────┐
│ 1. get_channels()          → đọc + chuẩn hoá link kênh              │
│ 2. list_recent_video_ids() → yt-dlp liệt kê video mỗi kênh          │
│ 3. extract_video()         → yt-dlp lấy caption + view/like/cmt     │
│ 4. keyword_filter          → giữ video khớp "qrevo 2 pro"           │
│ 5. excel_writer            → append (dedupe theo URL) → xlsx + csv  │
│ 6. metrics_refresher       → cào lại số liệu video ≤21 ngày         │
│ 7. summary_writer          → tổng hợp theo đại lý                   │
│ 8. report_html_builder     → dựng index.html (dashboard)           │
└────────────────────────────────────────────────────────────────────┘
        │  commit output/ + index.html
        ▼
GitHub repo (main) ──► GitHub Actions cron 17:15 VN ──► GitHub Pages
        │
        ▼
Dashboard công khai: https://tuananh-din.github.io/tiktok-dealer-tracker/
```

**Chạy ở đâu:** GitHub Actions (server GitHub), cron `15 10 * * *` UTC = **17:15 giờ
VN mỗi ngày**. Máy cá nhân tắt vẫn chạy. Có thể chạy tay: `python crawl.py`.

---

## 3. Tech stack

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12 (chỉ standard lib + yt-dlp + openpyxl) |
| Crawl | **yt-dlp** (lấy dữ liệu TikTok công khai, không cần API key) |
| Lưu trữ | Excel (openpyxl) + CSV; commit vào git |
| Input | Google Sheet công khai (CSV export) — không cần service account |
| Tự động hoá | GitHub Actions (cron hằng ngày) |
| Dashboard | HTML tĩnh tự sinh (Python f-string template) + GitHub Pages |
| Không dùng | database, backend server, framework JS — **toàn bộ tĩnh** |

---

## 4. Cấu trúc file

```
tiktok-dealer-tracker/
├── crawl.py                       # Điều phối toàn bộ pipeline
├── config.py                      # Cấu hình: keyword, nguồn, cửa sổ refresh...
├── channels.txt                   # Fallback list kênh (khi không dùng Sheet)
├── index.html                     # Dashboard công khai (TỰ SINH — không sửa tay)
├── bao-cao-qrevo2pro-tiktok.html  # Bản sao dashboard (tự sinh)
├── output/
│   ├── qrevo-videos.csv/.xlsx     # Dataset video (nguồn sự thật)
│   └── qrevo-summary.csv/.xlsx    # Tổng hợp theo đại lý
├── src/
│   ├── tiktok_crawler.py          # Bọc yt-dlp: list video, extract metadata
│   ├── keyword_filter.py          # Khớp từ khoá (bỏ dấu, linh hoạt khoảng trắng)
│   ├── channel_normalizer.py      # Chuẩn hoá link bẩn → URL kênh chuẩn
│   ├── sheet_reader.py            # Đọc kênh từ Google Sheet công khai
│   ├── excel_writer.py            # Ghi/append Excel, export CSV, dedupe URL
│   ├── metrics_refresher.py       # Cào lại view/like/cmt cho video ≤21 ngày
│   ├── summary_writer.py          # Tổng hợp per-đại-lý (view, eng%...)
│   ├── report_html_builder.py     # Tính toán + render dashboard HTML
│   ├── report_html_template.py    # CSS + khung HTML (str.format placeholders)
│   ├── pending_dealers.py         # Đại lý đăng ký nhưng CHƯA có video
│   └── weekly_winners.py          # ★ Honor roll đoạt giải theo tuần (đóng băng)
└── .github/workflows/crawl.yml    # GitHub Actions cron
```

---

## 5. Mô hình dữ liệu

### `output/qrevo-videos.csv` (mỗi dòng = 1 video)
`Collected Date | Channel | Keyword | Upload Date | Video URL | Caption | Views | Likes | Comments`
- `Channel` = handle TikTok của người đăng (vd `kimanh_1202`, không có `@`).
- Dedupe theo `Video URL`.

### Google Sheet (form đăng ký) — các cột chính
`Họ tên phụ trách | Tên cửa hàng/Đại lý | Tỉnh/TP | Đã có kênh chưa | Link kênh đã có | Link kênh mới tạo | ...`
> Lưu ý: tên người phụ trách + SĐT là **PII**, KHÔNG được đưa lên trang công khai.
> Dashboard chỉ hiển thị handle TikTok + tên cửa hàng + tỉnh.

### `src/weekly_winners.py` — dữ liệu đoạt giải (quan trọng cho tính năng mới)
```python
WEEKLY_WINNERS = [
    {
        "week": "Tuần 1",
        "range": "29/06 – 06/07/2026",
        "criteria": "≥ 10 video 'qrevo 2 pro' trong tuần",
        "dealers": [("kimanh_1202", 13), ("thurobot88", 13), ...],  # (handle, số video)
    },
    # thêm dict cho Tuần 2, 3... → dashboard tự hiện thêm
]
```

---

## 6. Tính năng dashboard hiện có

- **KPI**: tổng đại lý / video / view / like / comment / engagement%.
- **🏆 Vinh danh** (weekly winners honor roll) — huy chương 🥇🥈🥉 cho đại lý đạt giải.
- **Đà đăng tải theo tuần** (bar chart số video/tuần).
- **Pareto** — top đại lý gánh bao nhiêu % view.
- **Bảng xếp hạng** đại lý (video, view, TB view, eng%).
- **Chủ đề nội dung** (% caption nhắc giá/khuyến mãi, so sánh, review...).
- **Cảnh báo chất lượng** (% video <100 view, 0 comment...).
- **Top video hot nhất** (link TikTok).
- **Đề xuất hành động** (ưu tiên P1/P2/P3).
- **Đại lý đã đăng ký nhưng chưa có video** (nhắc kích hoạt).

---

## 7. Chương trình thi đua (award program)

- **Chu kỳ tuần** (Tuần 1: 29/6–6/7, Tuần 2 tiếp diễn...).
- **Tiêu chí:** đại lý đạt **≥10 video** "qrevo 2 pro"/tuần được vinh danh + thưởng.
- Team chủ động liên hệ winner để trao thưởng.
- Winner được đóng băng thủ công trong `weekly_winners.py` (award đã công bố
  thì không đổi kể cả dữ liệu cào lại sau đó có xê dịch).
- **Tuần 1 winners:** @kimanh_1202 (13), @thurobot88 (13), @phanthulan715 (13),
  @homecaredigital (11), @momimart.vn (11), @thietbibepan (10).

---

## 8. Trạng thái hiện tại (09/07/2026)

- ~**199 video**, ~**405.000 view**, **37 kênh** có video, **45+ đại lý** đăng ký.
- Kênh mạnh nhất: `minhchautestthat` (một clip so sánh Ecovacs vs Qrevo đạt >100k view).
- Dashboard live, tự cập nhật 17:15 VN mỗi ngày.

---

## 9. Ý tưởng mở rộng: trang "Gift / Celebration" cho winner

**Mục tiêu người dùng:** làm một web animation dạng "mở quà" — đại lý đoạt giải mở
link → **bắn pháo hoa, confetti, tung hô** chúc mừng, hiện tên kênh + số video +
huy chương + (tuỳ chọn) phần thưởng.

**Dữ liệu sẵn có để tái sử dụng:**
- Danh sách winner + handle + số video: `src/weekly_winners.py`.
- Có thể export thêm `output/winners.json` mỗi lần build để trang gift đọc.
- Toàn bộ hạ tầng là **tĩnh + GitHub Pages** → trang gift nên cùng dạng
  (self-contained HTML, không cần backend).

**Gợi ý kỹ thuật:** canvas fireworks/confetti (tsParticles hoặc canvas-confetti),
personalized URL per winner (vd `/gift/kimanh_1202`), nút "🎁 Mở quà" → reveal.
Có thể sinh ảnh certificate để winner share lên TikTok/Facebook → vòng lặp lan toả.

---

## 10. Ràng buộc & lưu ý

- **Không lộ PII** (tên người, SĐT) ra trang công khai — chỉ handle + tên cửa hàng + tỉnh.
- TikTok có thể chặn IP → yt-dlp đôi khi cần cookies (secret `TIKTOK_COOKIES`).
- Repo public → mọi file commit đều công khai.
- Toàn hệ thống ưu tiên **tĩnh, không backend, không DB** để chạy free trên GitHub.
