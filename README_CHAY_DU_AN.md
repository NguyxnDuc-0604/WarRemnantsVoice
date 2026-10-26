# 🎖️ WarRemnantsVoice — Hệ Thống Thuyết Minh Tự Động Đa Ngôn Ngữ
### Bảo Tàng Chứng Tích Chiến Tranh TP. Hồ Chí Minh (Theo Chuẩn PRD v1.0)

> **CƠ CHẾ HOẠT ĐỘNG CHUẨN PRD:**  
> Khách tham quan (Visitor) **KHÔNG CẦN CÀI APP**, **KHÔNG CẦN ĐĂNG KÝ TÀI KHOẢN**.  
> Chỉ cần mở **Ứng dụng Camera thông thường của điện thoại (iPhone / Android) hoặc ứng dụng Zalo**, quét mã QR dán trên tủ kính hoặc biển giới thiệu hiện vật. Trình duyệt điện thoại sẽ tự động mở trang thuyết minh đa ngôn ngữ, phát âm thanh và hiển thị phụ đề chạy đồng bộ theo lời đọc.

---

## 🚀 1. HƯỚNG DẪN KHỞI ĐỘNG HỆ THỐNG

Bạn chỉ cần chạy 2 file script `.bat` có sẵn:

### Bước 1: Khởi động Backend (FastAPI - Port 8000)
* Nhấp đúp chuột vào file: [`start_backend.bat`](file:///d:/VS%20Code/war-remnants-voice/start_backend.bat)
* Chờ terminal hiển thị: `INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

### Bước 2: Khởi động Frontend (React Vite - Port 5173)
* Nhấp đúp chuột vào file: [`start_frontend.bat`](file:///d:/VS%20Code/war-remnants-voice/start_frontend.bat)
* Chờ terminal hiển thị: `Local: http://localhost:5173/`

---

## 🛡️ 2. TRANG QUẢN TRỊ ADMIN (ADMIN CMS DASHBOARD)

Truy cập đường dẫn: **`http://localhost:5173/admin`** (hoặc bấm nút **Quản trị (Admin)** trên thanh menu).

Trang Quản trị cung cấp 2 tính năng trọng tâm:

### 📊 Tính năng 1: Thống Kê Số Người Đang Truy Cập Thời Gian Thực (UC5, FR-21, FR-22)
* 🟢 **Đang Truy Cập (Online Now):** Đếm chính xác số lượng du khách (CCU) đang mở ứng dụng trên điện thoại trong thời gian thực (tự động cập nhật mỗi 3 giây).
* 🎧 **Đang Nghe Thuyết Minh:** Số du khách đang bấm nút Play nghe giọng đọc AI.
* 📱 **Phân loại Thiết bị:** Tỷ lệ du khách dùng Mobile (điện thoại) so với Desktop (máy tính).
* 🌐 **Phân Bố Ngôn Ngữ:** Biểu đồ tỷ lệ du khách đang nghe tiếng gì (Anh, Pháp, Nhật, Hàn, Trung, Việt...).
* 👥 **Danh Sách Phiên Đang Kết Nối (Active Sessions):** Hiển thị chi tiết từng du khách đang xem hiện vật nào, nghe ngôn ngữ gì, dùng máy gì.
* 📜 **Nhật Ký Truy Cập Trực Tiếp (Live Activity Stream):** Theo dõi tức thì từng hành động của du khách khi quét mã QR vào bảo tàng.

### ➕ Tính năng 2: Thêm Hiện Vật Mới & Tự Động Sinh Mã QR (UC3, FR-02, FR-04)
1. Điền thông tin hiện vật: Mã hiện vật (`code`), Tên tiếng Việt, Tên tiếng Anh, Khu vực trưng bày, Thời kỳ lịch sử, Ảnh đại diện và Bài thuyết minh tiếng Việt chuẩn.
2. Bấm nút **"Lưu Hiện Vật & Kích Hoạt Mã QR"**:
   - Hệ thống lưu vào cơ sở dữ liệu.
   - **Tự động sinh ngay mã QR độ nét cao**.
   - Cung cấp nút **Tải ảnh mã QR PNG**, **Sao chép liên kết**, hoặc **Mở nghe thử trực tiếp**.

---

## 📱 3. CÁCH KIỂM THỬ NHIỀU ĐIỆN THOẠI CÙNG LÚC (KHÔNG CHUNG MẠNG 4G/5G)

Hệ thống cho phép **5, 10 hay hàng chục du khách dùng điện thoại 4G/5G hoặc mạng khác nhau** cùng quét mã QR và nghe thuyết minh cùng lúc.

### Bước 1: Mở đường link công khai ra Internet (Cloudflare Tunnel)
* Nhấp đúp vào file: [`start_public_tunnel.bat`](file:///d:/VS%20Code/war-remnants-voice/start_public_tunnel.bat)
* Terminal sẽ tạo ra một đường link HTTPS miễn phí, ví dụ:
  ```text
  https://spin-jewel-garden-adding.trycloudflare.com
  ```

### Bước 2: Hiển thị Biển Mã QR Hiện Vật trên máy tính
1. Mở trình duyệt máy tính vào: `http://localhost:5173/qr-stands`
2. Bấm nút **"🔗 Dán Link Cloudflare Tunnel (Cho điện thoại 4G/5G)"** và dán đường link `https://xxx.trycloudflare.com` vừa tạo.
3. Bấm **Áp dụng** $\rightarrow$ Toàn bộ mã QR của các hiện vật sẽ **tự động cập nhật ngay lập tức** theo link này!

### Bước 3: Lấy điện thoại quét mã QR trên màn hình máy tính
1. Cầm điện thoại (dùng 4G, 5G hoặc WiFi bất kỳ).
2. Mở ứng dụng **Camera chụp ảnh** hoặc **Zalo**.
3. Hướng camera vào mã QR của hiện vật trên màn hình máy tính.
4. Bấm vào liên kết xuất hiện trên màn hình điện thoại:
   - ✅ Điện thoại mở thẳng trang thuyết minh của hiện vật đó (thời gian nạp $\le 1.5$s).
   - ✅ Nhấn nút **"▶ Chạm để bắt đầu nghe thuyết minh"** để nghe âm thanh truyền cảm.
   - ✅ **Phụ đề tự động cuộn chữ và phát sáng theo từng câu đang đọc** (FR-16).
   - ✅ **Trên màn hình Admin (`/admin`), bạn sẽ thấy ngay số lượng "Người Đang Truy Cập (Online Now)" nhảy số lập tức!**

---

## 🗄️ 4. KIẾN TRÚC CƠ SỞ DỮ LIỆU CHUẨN PRD (PART III DATA DICTIONARY - 7 BẢNG)

Hệ thống triển khai đầy đủ 7 bảng dữ liệu theo đúng chuẩn tài liệu PRD Nhóm 3:

1. **`exhibit`** (Exhibit Core Service): Quản lý thông tin định danh hiện vật (`id`, `code`, `title`, `title_en`, `room_id`, `zone`, `latitude`, `longitude`, `radius`, `thumbnail_url`, `content_version`, `is_published`, `is_active`).
2. **`content_source`** (Nội dung nguồn tiếng Việt): Lưu trữ văn bản gốc chuẩn xác do bảo tàng phê duyệt (`original_text`, `original_audio_url`, `content_version`).
3. **`localization`** (Localization Service): Bản dịch và phụ đề đa ngôn ngữ (`exhibit_id`, `language_code`, `translated_title`, `translated_text`, `timestamps_json`, `is_reviewed`).
4. **`audio_media`** (Streaming & Media Service): Quản lý tệp âm thanh thuyết minh AI (`localization_id`, `file_url`, `storage_path`, `duration_seconds`, `bitrate_kbps`, `voice_code`, `status`).
5. **`tour_route`** (Tuyến tham quan chuyên đề): Lộ trình tham quan theo từng chủ đề lịch sử (`title`, `ordered_exhibits_json`, `estimated_time`).
6. **`glossary`** (Từ điển chuẩn hóa thuật ngữ lịch sử - quân sự): Chuẩn hóa các thuật ngữ nhạy cảm và địa danh lịch sử (`term_vi`, `term_en`, `context_note`, `is_restricted`).
7. **`listening_metric`** (Thống kê & Đo lường trải nghiệm): Số liệu thống kê lượt nghe ẩn danh phục vụ báo cáo quản trị (`exhibit_code`, `language_code`, `listened_duration`, `trigger_type`, `timestamp`).

### 🛠️ Cơ chế hoạt động kép (Dual DB Architecture):
* **Môi trường cục bộ không Docker:** Tự động sử dụng SQLite bền vững (`war_remnants_museum.db`) qua SQLAlchemy ORM với tính năng tự động tạo bảng (auto-DDL) và tự nạp dữ liệu mẫu khởi đầu (auto-seed) 5 hiện vật tiêu biểu, từ điển Glossary và 2 tour routes.
* **Môi trường Production / Docker Compose:** Sử dụng PostgreSQL chuẩn doanh nghiệp với script khởi tạo hoàn chỉnh tại [`database/init_database.sql`](file:///d:/VS%20Code/war-remnants-voice/database/init_database.sql) kết hợp `docker-compose.yml`.

---

*Hệ thống được phát triển bởi Nhóm 3 — Đồ án môn học Công Nghệ Phần Mềm (WarRemnantsVoice MVP v1.0)*
