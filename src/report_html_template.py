#!/usr/bin/env python3
"""CSS + HTML skeleton for the public report. Kept separate from the builder
logic so report_html_builder.py stays focused. Dynamic values are `{named}`
str.format placeholders; the CSS (which is full of braces) is injected as the
`{css}` value so its braces are never parsed by str.format."""

CSS = """
  :root{
    --navy:#0e1a2b; --ink:#1e293b; --muted:#64748b; --eye:#8a94a6;
    --line:#e2e8f0; --graybg:#f5f7fa; --track:#e6ecf3; --white:#ffffff;
    --blue:#2f6fed; --blue-bg:#e9f0fe; --blue-bd:#cadcfb;
    --green:#1f9d5f; --green-bg:#e7f6ed; --green-bd:#c2e7d0;
    --amber:#d9871a; --amber-bg:#fdf3e0; --amber-bd:#f2ddb2;
    --red:#e04d4d; --red-bg:#fdecec; --red-bd:#f6cccc;
  }
  *{box-sizing:border-box}
  body{margin:0;background:#e9edf2;color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14.5px;line-height:1.55}
  .wrap{max-width:1080px;margin:26px auto;background:var(--white);border-radius:18px;
    box-shadow:0 12px 44px rgba(15,25,45,.13);padding:34px 40px 40px;overflow:hidden}
  @media(max-width:720px){.wrap{padding:22px 18px;margin:12px}}
  a{color:var(--blue);text-decoration:none}
  a:hover{text-decoration:underline}
  h2.sec{font-size:19px;font-weight:800;margin:34px 0 4px;color:var(--navy);display:flex;align-items:center;gap:9px}
  h2.sec .bar{width:5px;height:20px;background:var(--blue);border-radius:3px}
  .sec-note{color:var(--muted);font-size:12.5px;margin:0 0 16px}
  .eyebrow{font-size:12px;font-weight:800;letter-spacing:1.3px;color:var(--eye);margin-bottom:12px}
  .title-band{background:var(--navy);border-radius:13px;padding:22px 26px}
  .title-band h1{margin:0;color:#fff;font-size:25px;font-weight:800;line-height:1.28}
  .title-band .sub{color:#a9b8cc;font-size:13.5px;margin-top:8px}
  .kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:18px}
  @media(max-width:820px){.kpis{grid-template-columns:repeat(3,1fr)}}
  @media(max-width:460px){.kpis{grid-template-columns:repeat(2,1fr)}}
  .kpi{border:1px solid var(--line);background:var(--graybg);border-radius:12px;padding:13px 14px}
  .kpi.b{background:var(--blue-bg);border-color:var(--blue-bd)}
  .kpi.g{background:var(--green-bg);border-color:var(--green-bd)}
  .kpi.a{background:var(--amber-bg);border-color:var(--amber-bd)}
  .kpi .k{font-size:10px;font-weight:800;letter-spacing:.4px;color:var(--muted);text-transform:uppercase}
  .kpi .v{font-size:22px;font-weight:800;margin-top:5px;color:var(--ink)}
  .kpi.b .v{color:var(--blue)} .kpi.g .v{color:var(--green)} .kpi.a .v{color:var(--amber)}
  .kpi .d{font-size:10.5px;color:var(--muted);margin-top:3px}
  .findings{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:6px}
  @media(max-width:760px){.findings{grid-template-columns:1fr}}
  .find{border-radius:12px;padding:15px 17px;border:1px solid var(--line)}
  .find.b{background:var(--blue-bg);border-color:var(--blue-bd)}
  .find.a{background:var(--amber-bg);border-color:var(--amber-bd)}
  .find.r{background:var(--red-bg);border-color:var(--red-bd)}
  .find .h{font-size:13px;font-weight:800;margin-bottom:5px}
  .find.b .h{color:var(--blue)} .find.a .h{color:#b56d0a} .find.r .h{color:#c23b3b}
  .find p{margin:0;font-size:12.6px;color:var(--ink);line-height:1.5}
  .find b{font-weight:800}
  .barlist{margin-top:6px}
  .bar-row{display:grid;grid-template-columns:160px 1fr 96px;align-items:center;gap:12px;margin:9px 0;font-size:13px}
  @media(max-width:600px){.bar-row{grid-template-columns:110px 1fr 84px}}
  .bar-row .nm{color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600}
  .bar-track{background:var(--track);border-radius:20px;height:20px;overflow:hidden}
  .bar-fill{display:block;height:100%;min-width:3px;border-radius:20px;background:linear-gradient(90deg,#2f6fed,#5b8bf5)}
  .bar-fill.g{background:linear-gradient(90deg,#1f9d5f,#43c383)}
  .bar-fill.a{background:linear-gradient(90deg,#d9871a,#efab4b)}
  .bar-row .vv{text-align:right;font-weight:800;font-variant-numeric:tabular-nums;color:var(--ink);font-size:12.5px}
  .bar-row .vv small{color:var(--muted);font-weight:600}
  .tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin-top:4px}
  table{width:100%;border-collapse:collapse;font-size:12.8px;min-width:640px}
  th,td{padding:9px 11px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
  th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}
  thead th{background:var(--navy);color:#dbe6f5;font-weight:700;font-size:10.5px;text-transform:uppercase;letter-spacing:.4px}
  tbody tr:nth-child(even){background:#fafbfd}
  tbody tr:hover{background:var(--blue-bg)}
  td .tag{display:inline-block;font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:10px;margin-left:6px;vertical-align:middle}
  .tag.reach{background:var(--blue-bg);color:var(--blue)}
  .tag.vol{background:#eee7fb;color:#6b46c8}
  .tag.eng{background:var(--green-bg);color:var(--green)}
  .tag.weak{background:var(--red-bg);color:var(--red)}
  td.eg-hi{color:var(--green);font-weight:800}
  td.eg-lo{color:var(--red);font-weight:700}
  .rk{color:var(--muted);font-weight:700}
  .leaders{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
  @media(max-width:760px){.leaders{grid-template-columns:1fr}}
  .lead{border:1px solid var(--line);border-radius:13px;padding:16px 17px;background:var(--white)}
  .lead .cap{font-size:11px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:var(--muted)}
  .lead .sub2{font-size:11px;color:var(--muted)}
  .lead .who{font-size:15px;font-weight:800;margin:5px 0 2px;color:var(--navy);word-break:break-all}
  .lead .big{font-size:26px;font-weight:800;margin:6px 0 0}
  .lead.blue .big{color:var(--blue)} .lead.purple .big{color:#6b46c8} .lead.green .big{color:var(--green)}
  .lead p{margin:8px 0 0;font-size:12px;color:var(--muted);line-height:1.5}
  .lead p b{color:var(--ink)}
  .callouts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
  @media(max-width:760px){.callouts{grid-template-columns:repeat(2,1fr)}}
  .call{border:1px solid var(--red-bd);background:var(--red-bg);border-radius:12px;padding:14px 15px;text-align:center}
  .call .n{font-size:25px;font-weight:800;color:var(--red)}
  .call .t{font-size:11.5px;color:#9a4a4a;margin-top:4px;font-weight:600}
  .vlist{margin-top:4px;border:1px solid var(--line);border-radius:12px;overflow:hidden}
  .vrow{display:grid;grid-template-columns:44px 1fr 130px;align-items:center;gap:12px;padding:11px 15px;border-bottom:1px solid var(--line);font-size:13px}
  .vrow:last-child{border-bottom:none}
  .vrow:nth-child(even){background:#fafbfd}
  .vrow .vn{font-size:17px;font-weight:800;color:var(--eye);text-align:center}
  .vrow .vc{overflow:hidden}
  .vrow .vc .cap{color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .vrow .vc .ch{color:var(--muted);font-size:11.5px}
  .vrow .vm{text-align:right;font-size:12px;color:var(--muted)}
  .vrow .vm b{color:var(--ink);font-size:14px}
  .recos{display:grid;gap:11px;margin-top:4px}
  .reco{display:grid;grid-template-columns:64px 1fr;gap:14px;align-items:start;
    border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--graybg)}
  .reco .pri{font-size:11px;font-weight:800;padding:5px 0;text-align:center;border-radius:8px;color:#fff}
  .reco .pri.p1{background:var(--red)} .reco .pri.p2{background:var(--amber)} .reco .pri.p3{background:var(--blue)}
  .reco .rc h4{margin:0 0 4px;font-size:14px;font-weight:800;color:var(--navy)}
  .reco .rc p{margin:0;font-size:12.7px;color:var(--ink);line-height:1.5}
  .reco .rc b{font-weight:800}
  footer{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:11.5px;line-height:1.6}
  .pill{display:inline-block;background:var(--blue-bg);border:1px solid var(--blue-bd);color:var(--blue);
    font-size:11.5px;font-weight:700;padding:5px 13px;border-radius:20px;margin-top:14px}
  table.pend{min-width:520px}
  table.pend th,table.pend td{text-align:left;white-space:normal}
  table.pend td.rk{white-space:nowrap;color:var(--muted);font-weight:700}
  table.pend td.ch{white-space:nowrap}
  table.pend td.ch a{font-weight:700;margin-right:8px;display:inline-block}
  .honor{border:1px solid var(--amber-bd);border-radius:14px;padding:20px 22px;margin-top:6px;
    background:linear-gradient(135deg,#fff9ee,#fdf3e0)}
  .honor .hh{font-size:16px;font-weight:800;color:#b56d0a;display:flex;flex-wrap:wrap;
    align-items:baseline;gap:8px}
  .honor .hh small{font-weight:700;color:var(--muted);font-size:12px}
  .honor .crit{font-size:12px;color:var(--muted);margin:3px 0 14px}
  .winners{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  @media(max-width:640px){.winners{grid-template-columns:repeat(2,1fr)}}
  @media(max-width:400px){.winners{grid-template-columns:1fr}}
  .win{background:var(--white);border:1px solid var(--amber-bd);border-radius:12px;
    padding:14px 12px;text-align:center;position:relative}
  .win.g1{border-color:#e6b800;box-shadow:0 2px 10px rgba(214,158,0,.18)}
  .win .medal{font-size:24px;line-height:1}
  .win .who{font-weight:800;color:var(--navy);font-size:14px;margin-top:6px;word-break:break-all}
  .win .who a{color:var(--navy)}
  .win .cnt{font-size:26px;font-weight:800;color:var(--amber);margin-top:3px;line-height:1.1}
  .win .cnt small{font-size:11px;font-weight:700;color:var(--muted)}
  .win .giftlink{display:inline-block;margin-top:9px;font-size:11.5px;font-weight:800;
    color:#b56d0a;background:#fff7e6;border:1px solid var(--amber-bd);border-radius:999px;
    padding:5px 12px;text-decoration:none}
  .win .giftlink:hover{background:#ffefc9;text-decoration:none}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Báo cáo Chương trình TikTok Đại lý — Qrevo 2 Pro</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">

  <div class="eyebrow">QREVO 2 PRO&nbsp;&nbsp;·&nbsp;&nbsp;CHƯƠNG TRÌNH TIKTOK ĐẠI LÝ&nbsp;&nbsp;·&nbsp;&nbsp;BÁO CÁO PHÂN TÍCH</div>
  <div class="title-band">
    <h1>Chương trình kích hoạt {n_dealers} đại lý &amp; {tot_v} video —<br>Top 3 đại lý đang chiếm {top3_view_pct}% lượt xem</h1>
    <div class="sub">Theo dõi tự động video đại lý nhắc từ khoá “qrevo 2 pro” · Kỳ dữ liệu {period} · số liệu &amp; phân tích tự tính lại mỗi ngày</div>
  </div>

  <div class="kpis">
    <div class="kpi b"><div class="k">Đại lý</div><div class="v">{n_dealers}</div><div class="d">kênh active</div></div>
    <div class="kpi g"><div class="k">Video</div><div class="v">{tot_v}</div><div class="d">qrevo 2 pro</div></div>
    <div class="kpi a"><div class="k">Lượt xem</div><div class="v">{tot_view}</div><div class="d">TB {avg} · trung vị {median}</div></div>
    <div class="kpi"><div class="k">Lượt thích</div><div class="v">{tot_like}</div><div class="d">tym</div></div>
    <div class="kpi"><div class="k">Bình luận</div><div class="v">{tot_cmt}</div><div class="d">comment</div></div>
    <div class="kpi"><div class="k">Tương tác</div><div class="v">{eng}%</div><div class="d">(tym+cmt)/view</div></div>
  </div>
{winners_section}
  <h2 class="sec"><span class="bar"></span>Điểm nhấn</h2>
  <p class="sec-note">3 điều quan trọng nhất rút ra từ dữ liệu kỳ này.</p>
  <div class="findings">
    <div class="find b">
      <div class="h">📈 Đà đăng tải</div>
      <p>Tuần gần nhất có <b>{last_ct} video</b> — chiếm <b>{last_pct}%</b> toàn bộ nội dung kỳ. Xem cột “Đà theo tuần” bên dưới để biết đang tăng hay giảm.</p>
    </div>
    <div class="find a">
      <div class="h">🎯 Độ phủ dồn vào số ít</div>
      <p>Top 3 đại lý hút <b>{top3_view_pct}% lượt xem</b>; riêng <b>{reach_ch} chiếm {top1_view_pct}%</b>. Rủi ro phụ thuộc — cần nhân rộng ra nhóm giữa.</p>
    </div>
    <div class="find r">
      <div class="h">⚠️ Chất lượng còn mỏng</div>
      <p><b>{low100_pct}%</b> video &lt;100 view, <b>{zerocmt_pct}%</b> video không có bình luận, <b>{dealers_le2}/{n_dealers}</b> đại lý đăng ≤2 video.</p>
    </div>
  </div>

  <h2 class="sec"><span class="bar"></span>Đà đăng tải theo tuần</h2>
  <p class="sec-note">Số video đăng mỗi tuần (theo ngày đăng thực tế).</p>
  <div class="barlist">
{weekly_bars}
  </div>

  <h2 class="sec"><span class="bar"></span>Mức độ tập trung (Pareto)</h2>
  <p class="sec-note">Ai đang gánh lượt xem cho cả chương trình.</p>
  <div class="barlist">
{conc_bars}
  </div>

  <h2 class="sec"><span class="bar"></span>Bảng xếp hạng {n_dealers} đại lý</h2>
  <p class="sec-note">Sắp theo lượt xem. <b>TB view</b> = view / video (thước đo chất lượng nội dung). Eng% có dấu * = nền view quá nhỏ, dễ nhiễu.</p>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>#</th><th>Đại lý</th><th>Video</th><th>View</th><th>TB view</th><th>Tym</th><th>Cmt</th><th>Eng%</th></tr></thead>
      <tbody>
{leaderboard}
      </tbody>
    </table>
  </div>
{pending_section}
  <h2 class="sec"><span class="bar"></span>Ba nhà vô địch — ba thế mạnh khác nhau</h2>
  <p class="sec-note">Không có “đại lý tốt nhất” tuyệt đối — mỗi kênh mạnh một trục. Học từ cả ba.</p>
  <div class="leaders">
    <div class="lead blue">
      <div class="cap">📢 Độ phủ (Reach)</div>
      <div class="who">{reach_ch}</div>
      <div class="big">{reach_avg}</div>
      <div class="sub2">view / video · gấp {reach_mult}× TB</div>
      <p><b>Nội dung chuẩn nhất.</b> Hút {reach_view_pct}% tổng view. Nhưng eng chỉ {reach_eng}% — kiểu “phát sóng”, ít tương tác.</p>
    </div>
    <div class="lead purple">
      <div class="cap">🔁 Sản lượng (Volume)</div>
      <div class="who">{vol_ch}</div>
      <div class="big">{vol_v}</div>
      <div class="sub2">video · nhiều nhất kỳ</div>
      <p><b>Chăm nhất</b> (eng {vol_eng}%). TB {vol_avg} view/video — chú ý cân bằng số lượng với chất lượng.</p>
    </div>
    <div class="lead green">
      <div class="cap">❤️ Tương tác (Engage)</div>
      <div class="who">{eng_ch}</div>
      <div class="big">{eng_val}%</div>
      <div class="sub2">{eng_like} tym + {eng_cmt} cmt / {eng_view} view</div>
      <p><b>Cộng đồng “chạm” nhất.</b> {eng_v} video tạo nhiều hội thoại — mời chia sẻ công thức khơi bình luận.</p>
    </div>
  </div>

  <h2 class="sec"><span class="bar"></span>Nội dung đại lý đang nói gì?</h2>
  <p class="sec-note">% video có nhắc chủ đề trong caption (1 video có thể thuộc nhiều chủ đề).</p>
  <div class="barlist">
{themes_bars}
  </div>
  <div class="find a" style="margin-top:14px">
    <div class="h">🔎 Khoảng trống nội dung</div>
    <p>Nội dung nghiêng về chức năng sản phẩm, nhưng thiếu tầng chốt sale: chỉ <b>{price}% nhắc giá/khuyến mãi</b>, <b>{comp}% so sánh</b>. Bổ sung CTA + giá + so sánh để chuyển view → khách.</p>
  </div>

  <h2 class="sec"><span class="bar"></span>Cảnh báo chất lượng</h2>
  <p class="sec-note">Những con số cần chú ý để chương trình đi vào chiều sâu.</p>
  <div class="callouts">
    <div class="call"><div class="n">{low100_pct}%</div><div class="t">video &lt;100 view<br>({low100}/{tot_v})</div></div>
    <div class="call"><div class="n">{zerocmt_pct}%</div><div class="t">video 0 bình luận<br>({zerocmt}/{tot_v})</div></div>
    <div class="call"><div class="n">{dealers_le2}/{n_dealers}</div><div class="t">đại lý đăng ≤2 video<br>rồi dừng</div></div>
    <div class="call"><div class="n">{median}</div><div class="t">view trung vị<br>(&lt; TB {avg} → lệch top)</div></div>
  </div>

  <h2 class="sec"><span class="bar"></span>Top video hot nhất kỳ</h2>
  <p class="sec-note">Sắp theo lượt xem. Bấm để xem video trên TikTok.</p>
  <div class="vlist">
{top_videos}
  </div>

  <h2 class="sec"><span class="bar"></span>Đề xuất hành động (ưu tiên)</h2>
  <p class="sec-note">Sắp theo tác động × độ dễ triển khai.</p>
  <div class="recos">
{recos}
  </div>

  <footer>
    <b>Nguồn:</b> TikTok Dealer Video Tracker (yt-dlp · dữ liệu công khai TikTok) · <b>Kỳ:</b> {period} · <b>Cập nhật:</b> {snapshot}.<br>
    <b>Cách đọc:</b> KPI chính là độ phủ (view) &amp; tương tác. Eng% = (tym+cmt)/view; với đại lý ít view chỉ số này dễ nhiễu (đánh dấu *), nên đọc kèm số tuyệt đối.
    <div class="pill">🔄 Trang tự tính lại số liệu &amp; phân tích mỗi ngày ~17:15 (giờ VN)</div>
  </footer>

</div>
</body>
</html>
"""
