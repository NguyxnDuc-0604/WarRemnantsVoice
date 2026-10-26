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
* Chờ terminal hiển thị: `Uvicorn running on http://0.0.0.0:8000`

### Bước 2: Khởi động Frontend (React Vite - Port 5173)
* Nhấp đúp chuột vào file: [`start_frontend.bat`](file:///d:/VS%20Code/war-remnants-voice/start_frontend.bat)
* Chờ terminal hiển thị: `Local: http://localhost:5173/`

---

## 📱 2. CÁCH KIỂM THỬ NHIỀU ĐIỆN THOẠI CÙNG LÚC (KHÔNG CHUNG MẠNG 4G/5G)

Hệ thống cho phép **5, 10 hay hàng chục du khách dùng điện thoại 4G/5G hoặc mạng khác nhau** cùng quét mã QR và nghe thuyết minh cùng lúc.

### Bước 1: Mở đường link công khai ra Internet (Cloudflare Tunnel)
* Nhấp đúp vào file: [`start_public_tunnel.bat`](file:///d:/VS%20Code/war-remnants-voice/start_public_tunnel.bat)
* Terminal sẽ tạo ra một đường link HTTPS miễn phí, ví dụ:
  ```text
  https://war-remnants-sample.trycloudflare.com
  ```

### Bước 2: Hiển thị Biển Mã QR Hiện Vật trên máy tính
1. Mở trình duyệt máy tính vào: `http://localhost:5173/qr-stands`
2. Bấm nút **"Đổi Domain Tunnel (4G/5G)"** và dán đường link `https://war-remnants-sample.trycloudflare.com` vừa tạo được ở Bước 1.
3. Toàn bộ mã QR của các hiện vật (*Máy bay UH-1, Xe tăng T-54B số hiệu 390, Chuồng cọp Côn Đảo...*) sẽ **tự động cập nhật ngay lập tức** theo đường link này!

### Bước 3: Lấy điện thoại quét mã QR trên màn hình máy tính
1. Cầm điện thoại (dùng 4G, 5G hoặc WiFi bất kỳ).
2. Mở ứng dụng **Camera chụp ảnh** hoặc **Zalo**.
3. Hướng camera vào mã QR của hiện vật trên màn hình máy tính.
4. Bấm vào liên kết xuất hiện trên màn hình điện thoại:
   - ✅ Điện thoại mở thẳng trang thuyết minh của hiện vật đó (thời gian nạp $\le 1.5$s).
   - ✅ Tự động nạp bản dịch và giọng đọc AI (Microsoft Edge TTS Neural).
   - ✅ Nhấn nút **"▶ Chạm để bắt đầu nghe thuyết minh"** để nghe âm thanh truyền cảm, trang nghiêm.
   - ✅ **Phụ đề tự động cuộn chữ và phát sáng theo từng câu đang đọc** (FR-16).
   - ✅ Có thể chuyển đổi tức thì giữa 15 ngôn ngữ quốc tế (Anh, Pháp, Nhật, Hàn, Trung, Đức, Nga, Tây Ban Nha...).
   - ✅ Hệ thống tự động ghi nhớ ngôn ngữ cho các lần quét hiện vật tiếp theo (FR-07).

---

## 🏛️ 3. DANH SÁCH HIỆN VẬT MẪU TRONG HỆ THỐNG

| Mã Code | Mã Hiển Thị | Tên Hiện Vật | Khu Vực Trưng Bày | Link Truy Cập Trực Tiếp |
|:---:|:---:|:---|:---|:---|
| `UH1-BELL` | `EX-01` | Máy bay trực thăng UH-1 Iroquois 'Huey' | Ngoài trời | `/exhibit/UH1-BELL` |
| `T54-390` | `EX-02` | Xe tăng T-54B số hiệu 390 (Húc đổ cổng Dinh Độc Lập) | Sân cơ giới ngoài trời | `/exhibit/T54-390` |
| `M107-175` | `EX-03` | Pháo tự hành M107 175mm 'Vua chiến trường' | Bãi pháo binh ngoài trời | `/exhibit/M107-175` |
| `CONDAO-CAGE` | `EX-04` | Mô hình phục dựng Chuồng cọp Côn Đảo | Phòng chứng tích tội ác | `/exhibit/CONDAO-CAGE` |
| `HOCHIMINH-CAMPAIGN` | `EX-05` | Sa bàn Chiến dịch Hồ Chí Minh lịch sử | Phòng lịch sử tổng hợp | `/exhibit/HOCHIMINH-CAMPAIGN` |

---

## ⚙️ 4. TÍNH NĂNG ĐÁP ỨNG ĐÚNG CHUẨN PRD

* **FR-05 & UC1 (Nhận diện qua QR):** Đường link QR dạng `https://<domain>/exhibit/:code` không mang dữ liệu nặng, API Gateway giải mã và mở trang trong $\le 1.5$ giây.
* **BR-07 (Không yêu cầu đăng nhập):** Khách quét QR là nghe được ngay, bảo vệ quyền riêng tư tuyệt đối (BR-15).
* **BR-10 (Tương thích Autoplay):** Nút chạm to bản vượt qua rào cản chặn phát âm thanh của trình duyệt di động (iOS Safari, Android Chrome).
* **FR-16 (Đồng bộ phụ đề thời gian thực):** Mốc thời gian `timestamps_json` được tính toán chính xác; câu đang đọc sáng màu vàng hổ phách và tự động cuộn chữ vào giữa màn hình.
* **FR-17 (Điều khiển linh hoạt):** Hỗ trợ nút tua tới/lui 10s (`-10s`, `+10s`), điều chỉnh tốc độ đọc (`0.8x`, `1.0x`, `1.2x`), chạm trực tiếp vào câu trong phụ đề để tua nhanh âm thanh đến đoạn đó.
* **UC2 (Tham quan theo lộ trình):** Nút gợi ý *"Điểm tham quan kế tiếp"* ở cuối trang giúp du khách di chuyển liên tục theo mạch lịch sử mà không cần quét lại nếu không muốn.
* **FR-20 & BR-15 (Thống kê ẩn danh):** Tự động ghi nhận thời lượng nghe thực tế vào hệ thống sau khi nghe xong bài.

---

*Hệ thống được phát triển bởi Nhóm 3 — Đồ án môn học Công Nghệ Phần Mềm (WarRemnantsVoice MVP v1.0)*
