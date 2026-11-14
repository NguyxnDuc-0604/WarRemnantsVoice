# 📱 Giải Pháp Truy Cập Tức Thì Cho Điện Thoại (Không Nhập IP / Password)

## ❌ NGUYÊN NHÂN GÂY RA HIỆN TƯỢNG BẮT NHẬP "IP PUBLIC / TUNNEL PASSWORD"

Khi sử dụng công cụ **LocalTunnel** (`localtunnel / loca.lt`), dịch vụ này có một cơ chế chống lạm dụng (anti-abuse reminder) yêu cầu người truy cập lần đầu phải nhập địa chỉ IP Public của máy chủ thì mới cho vào web.

👉 **Đối với du khách bảo tàng:** Đây là một rào cản rất lớn, vì khách chỉ muốn quét mã QR là nghe được ngay, không ai muốn và không ai biết IP Public để nhập!

---

## ✅ GIẢI PHÁP TRIỆT ĐỂ: SỬ DỤNG CLOUDFLARE TUNNEL (ĐÃ TẢI SẴN TRONG DỰ ÁN)

Tôi đã tải sẵn tệp tin thực thi chính thức [`cloudflared.exe`](file:///d:/VS%20Code/war-remnants-voice/cloudflared.exe) trực tiếp vào thư mục dự án của bạn.

### Ưu điểm vượt trội của Cloudflare Tunnel:
* ✅ **MỞ THẲNG 100%:** Khách dùng Camera điện thoại hoặc Zalo quét mã QR là **vào thẳng bài thuyết minh ngay lập tức**.
* ✅ **TUYỆT ĐỐI KHÔNG BẮT NHẬP GÌ:** Không hỏi IP, không hỏi Password, không có màn hình cảnh báo hay xác nhận trung gian.
* ✅ **CÓ SẴN HTTPS CHUẨN:** Đảm bảo âm thanh và trình phát PWA chạy mượt mà trên cả iOS Safari và Android Chrome.
* ✅ **HOÀN TOÀN MIỄN PHÍ & KHÔNG GIỚI HẠN:** Bao nhiêu điện thoại dùng 4G/5G cùng quét một lúc cũng được.

---

## 🚀 QUY TRÌNH THỰC HIỆN 3 BƯỚC ĐƠN GIẢN

### Bước 1: Khởi động Backend & Frontend
* Bật [`start_backend.bat`](file:///d:/VS%20Code/war-remnants-voice/start_backend.bat) (Port 8000)
* Bật [`start_frontend.bat`](file:///d:/VS%20Code/war-remnants-voice/start_frontend.bat) (Port 5173)

### Bước 2: Bật Cloudflare Tunnel
Nhấp đúp chuột vào file:
👉 [`start_public_tunnel.bat`](file:///d:/VS%20Code/war-remnants-voice/start_public_tunnel.bat)

Chờ khoảng 5–10 giây, trên màn hình console sẽ hiện ra đường link dạng:
```text
https://something-random.trycloudflare.com
```
*(Copy dòng link này lại)*

### Bước 3: Cập nhật đường link vào Bảng Mã QR trên máy tính
1. Mở trình duyệt máy tính vào: `http://localhost:5173/qr-stands`
2. Bấm nút **"🔗 Dán Link Cloudflare Tunnel (Cho điện thoại 4G/5G)"**.
3. Dán đường link `https://xxx.trycloudflare.com` vừa copy ở Bước 2 vào ô $\rightarrow$ Bấm **Áp dụng**.
4. Toàn bộ các mã QR trên màn hình máy tính sẽ tự động cập nhật ngay lập tức theo link này.

### Bước 4: Kiểm thử trên điện thoại (4G / 5G)
1. Cầm điện thoại (dùng 4G/5G hoặc WiFi bất kỳ).
2. Bật **Camera chụp ảnh của điện thoại** hoặc **Zalo**.
3. Lia camera vào mã QR của hiện vật trên màn hình máy tính.
4. Chạm vào liên kết:
   * **Kết quả:** Điện thoại mở thẳng trang thuyết minh của hiện vật!
   * **Tuyệt đối không có bất kỳ màn hình hỏi IP hay mật khẩu nào!**
   * Bấm nút **"▶ Chạm để bắt đầu nghe thuyết minh"** để nghe giọng đọc AI và xem phụ đề chạy chữ song ngữ.
