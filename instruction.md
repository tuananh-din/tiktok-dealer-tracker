# TikTok Dealer Tracker — Hướng dẫn phát triển

Tài liệu này là điểm bắt đầu cho bất kỳ ai hoặc AI nào cần bảo trì hay phát
triển dự án. Đọc trước khi sửa tính năng, dữ liệu hoặc lịch chạy.

## Mục tiêu

Theo dõi video TikTok của đại lý có nhắc `qrevo 2 pro`, công bố báo cáo công
khai và vinh danh người đạt từ 10 video mỗi tuần. Hệ thống ưu tiên tĩnh, không
có backend/database và không đưa PII (họ tên, số điện thoại) lên website.

## Kiến trúc

```text
Google Sheet đăng ký đại lý
        ↓
crawl.py + yt-dlp (GitHub Actions mỗi ngày)
        ↓
output/qrevo-videos.csv + .xlsx
        ↓
summary / weekly winners / report builder
        ↓
index.html + celebrate.html + output/*.json
        ↓
GitHub Pages
```

Trang công khai: https://tuananh-din.github.io/tiktok-dealer-tracker/

## Tệp quan trọng

| Tệp | Vai trò |
| --- | --- |
| `config.py` | Nguồn kênh, từ khóa, số video/kênh, output và cửa sổ refresh. |
| `crawl.py` | Pipeline chính: crawl, lưu dữ liệu, chốt tuần, export JSON và dựng HTML. |
| `src/tiktok_crawler.py` | Lớp gọi yt-dlp; tự chọn executable tương thích Windows/Linux. |
| `src/weekly_winners.py` | Luật tuần, dữ liệu vinh danh nền và cơ chế tự chốt các tuần đã kết thúc. |
| `output/weekly-winners.json` | Snapshot vinh danh bất biến được GitHub Actions commit; nguồn sự thật cho các tuần đã công bố. |
| `src/winners_export.py` | Chuyển snapshot thành `output/winners.json` cho celebrate. |
| `src/report_html_builder.py` | Dựng dashboard `index.html` và bản sao báo cáo. |
| `celebrate.html` | Trang chúc mừng cá nhân: `?dealer=<handle>`. |
| `.github/workflows/crawl.yml` | Lịch chạy, secrets, commit/push kết quả. |

## Dữ liệu và quy tắc giải

- Nguồn thật: `output/qrevo-videos.csv`; mỗi dòng là một video, không trùng URL.
- Một tuần đủ 7 ngày, từ thứ Hai đến Chủ nhật; Tuần 3 bắt đầu 13/07/2026.
- Điều kiện giải: ít nhất 10 video có từ khóa trong tuần.
- Tối đa 6 người thắng. Sắp xếp theo số video giảm dần; nếu bằng nhau, người đạt
  video thứ 10 sớm hơn được ưu tiên; sau đó dùng handle để kết quả luôn ổn định.
- Khi một tuần được chốt, snapshot không đổi dù view/like/comment được refresh
  về sau.
- Không đưa PII vào dashboard, JSON public hoặc URL chúc mừng.

## Tự động hóa và chống bỏ lỡ tuần

GitHub Actions là nguồn chạy chính, không phụ thuộc máy cá nhân.

- Crawler chạy mỗi ngày lúc 17:15 giờ Việt Nam.
- Có lượt dự phòng vào 18:45 thứ Hai để bảo vệ thời điểm chốt tuần.
- Sau mỗi crawl thành công, `freeze_completed_weeks()` kiểm tra mọi tuần đã kết
  thúc nhưng chưa có snapshot. Nếu lịch thứ Hai bị trễ hoặc bị bỏ lỡ, lần chạy
  sau tự bù tuần còn thiếu.
- Nếu tuần đó chưa có dữ liệu video (ví dụ TikTok bị chặn), hệ thống không công
  bố kết quả rỗng; giữ tuần ở trạng thái chờ và thử lại ở lượt kế tiếp.
- Kết quả được ghi vào `output/weekly-winners.json`, sau đó tạo
  `output/winners.json`, dashboard và trang celebrate cùng một lượt.
- Workflow retry `pull --rebase` + `push` tối đa ba lần. Nếu vẫn không xuất bản
  được, job phải thất bại rõ ràng thay vì bỏ qua lỗi push.

### Secrets cần có trên GitHub

| Secret | Bắt buộc | Dùng cho |
| --- | --- | --- |
| `GSHEET_ID` | Có nếu dùng Google Sheet | Danh sách kênh/đầu vào. |
| `GOOGLE_CREDENTIALS` | Chỉ khi dùng Google Sheets private | Service account. |
| `TIKTOK_COOKIES` | Khuyến nghị | Giảm rủi ro TikTok chặn crawler trên GitHub. |

## Kiểm tra sau mỗi thay đổi

1. Kiểm tra cú pháp: `python -m py_compile crawl.py src/*.py`.
2. Chạy thử crawler khi cần: `python crawl.py`.
3. Kiểm tra `output/winners.json`, đặc biệt tuần mới có handle, số video và rank đúng.
4. Mở `index.html`: phần “Vinh danh” phải có tuần mới.
5. Mở `celebrate.html?dealer=<handle>`: phải hiển thị đúng tuần, huy chương và số video.
6. Sau khi push, kiểm tra GitHub Actions đã xanh và mở lại GitHub Pages với hard refresh.

## Khi phát triển tính năng mới

- Giữ website tĩnh, chỉ dùng JSON/CSV public-safe; không thêm backend nếu không cần.
- Nếu thêm dữ liệu public, cập nhật cả builder, export JSON và tài liệu này.
- Nếu thay luật giải, sửa `WEEK_THRESHOLD`, logic xếp hạng và mô tả trên dashboard
  cùng một thay đổi; không sửa snapshot đã công bố trừ khi có quyết định nghiệp vụ.
- Nếu thêm một trang, dùng dữ liệu từ `output/` và liên kết tương đối để GitHub
  Pages hoạt động.
- Không chỉnh tay `index.html` hoặc `bao-cao-qrevo2pro-tiktok.html`: chúng là tệp
  sinh tự động. Sửa builder/template rồi dựng lại.
- `celebrate.html` có dữ liệu fallback cho tình huống fetch JSON thất bại; khi đổi
  giao diện hoặc format winner, cập nhật fallback tương ứng.

## Xử lý sự cố nhanh

| Triệu chứng | Kiểm tra/khắc phục |
| --- | --- |
| Pages vẫn là tuần cũ | Kiểm tra Actions, commit mới trên `main`, sau đó hard refresh; Pages có thể cần vài phút để triển khai. |
| Không có kết quả tuần mới | Kiểm tra `output/qrevo-videos.csv` có video đúng khoảng ngày chưa; xem log Actions và `TIKTOK_COOKIES`. |
| Windows báo `WinError 193` | Cập nhật `src/tiktok_crawler.py`; không dùng executable `.venv/bin/yt-dlp` của macOS/Linux trên Windows. |
| Push bị từ chối | Không force-push. Fetch/pull --rebase, giải quyết khác biệt dữ liệu rồi push lại. |
| Một tuần bị lỡ | Chạy workflow thủ công; finalizer sẽ tự bù tuần chưa có trong `output/weekly-winners.json`. |

## Trạng thái mẫu đã chốt

Tuần 4, 20/07–26/07/2026:

1. `@phanthulan715` — 15 video
2. `@3t.smart.robot.tn` — 13 video
3. `@.hng0863` — 11 video

