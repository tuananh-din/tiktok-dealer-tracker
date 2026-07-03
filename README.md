# TikTok Dealer Video Tracker

Crawl video từ list kênh TikTok đại lý, **bắt từ khoá `qrevo 2 pro`** trong caption,
gom **link + caption** (kèm ngày đăng, views, likes, comments) và ghi ra báo cáo.
Chạy tự động **hằng ngày 17h (giờ VN) trên GitHub Actions — không cần bật máy**.

## Chạy ở đâu?
GitHub Actions (server của GitHub). Máy bạn tắt vẫn chạy. Kết quả được **commit
thẳng vào repo** (Excel + CSV — xem được như bảng trên GitHub), hoặc đẩy sang
**Google Sheet** (tuỳ chọn, sau khi cấp credentials).

## Cấu hình nguồn/đích — `config.py`
```python
CHANNELS_SOURCE = "file"          # "file" | "google_sheets"
OUTPUTS         = ["excel"]        # ["excel"], ["google_sheets"], hoặc cả hai
KEYWORDS        = ["qrevo 2 pro"]  # thêm biến thể tuỳ ý
```

## Chế độ A — GitHub log (mặc định, KHÔNG cần Google)
1. Thêm kênh vào `channels.txt` (mỗi dòng 1 `@handle` hoặc URL).
2. Push. GitHub Actions chạy 17h/ngày → ghi `output/qrevo-videos.csv` + `.xlsx`
   và commit vào repo.
3. Xem báo cáo: mở `output/qrevo-videos.csv` trên GitHub (render dạng bảng).

## Chế độ B — Google Sheet (input + báo cáo trên Sheet)
Cần 1 lần cấp quyền (chỉ bạn làm được — Google yêu cầu tài khoản của bạn):
1. Tạo **service account** (Google Cloud) + bật **Google Sheets API**, tải file JSON.
2. Tạo Google Sheet, tab `channels` (cột A = list kênh), share Sheet cho email
   service account (quyền Editor). Lấy **Spreadsheet ID** từ URL.
3. Trong repo GitHub: **Settings → Secrets → Actions** thêm:
   - `GOOGLE_CREDENTIALS` = toàn bộ nội dung file JSON.
4. Trong `config.py`: đặt `GSHEET_ID`, đổi `CHANNELS_SOURCE = "google_sheets"`,
   `OUTPUTS = ["google_sheets"]`. Push.
> Báo cáo sẽ tự ghi sang tab `videos`, chống trùng theo URL.

## Chạy thử tại máy (tuỳ chọn)
```bash
cd tiktok-dealer-tracker
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python crawl.py
```

## Chỉnh lịch chạy
Sửa cron trong `.github/workflows/crawl.yml`:
- `0 10 * * *` = 17:00 VN mỗi ngày (UTC+7).
- Bỏ comment dòng `*/30 * * * *` để chạy mỗi 30 phút (near-realtime).

## Cột báo cáo
`Collected Date | Channel | Keyword | Upload Date | Video URL | Caption | Views | Likes | Comments`

## Lưu ý thật
- yt-dlp lấy dữ liệu **công khai**, không cần API key. TikTok có thể chặn IP
  datacenter của GitHub → nếu bị chặn, thêm secret `TIKTOK_COOKIES` (cookies.txt
  dạng Netscape export từ trình duyệt đã đăng nhập TikTok).
- Kênh nào lỗi thì bỏ qua, không dừng cả run.
- "Realtime" thực chất là batch theo lịch; GitHub Actions có thể trễ vài phút.
