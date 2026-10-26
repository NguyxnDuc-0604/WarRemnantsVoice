# 📱 Hướng Dẫn Truy Cập Nhiều Điện Thoại Cùng Lúc (Không Chung Mạng)

Tài liệu này hướng dẫn chi tiết cách chia sẻ ứng dụng **WarRemnantsVoice** ra Internet để **nhiều người dùng điện thoại sử dụng 4G/5G hoặc mạng WiFi khác cùng lúc** có thể truy cập, quét mã QR và nghe thuyết minh bảo tàng.

---

## ⚠️ Điểm Mấu Chốt Về Camera & Quét Mã QR

> **LƯU Ý CỰC KỲ QUAN TRỌNG:**
> Các trình duyệt hiện đại trên điện thoại (**iOS Safari**, **Android Chrome**, Samsung Internet...) **BẮT BUỘC kết nối phải có HTTPS** (hoặc `localhost`) thì mới cho phép cấp quyền mở **Camera**.
> 
> Nếu chỉ mở qua `http://192.168.x.x` thông thường, trình duyệt điện thoại sẽ chặn không cho mở Camera để quét mã QR!
> 
> 👉 Do đó, các giải pháp Tunnel có sẵn **HTTPS miễn phí** dưới đây là cách hoàn hảo nhất: vừa mở được từ xa qua 4G/5G, vừa cho phép quét mã QR bằng camera trơn tru!

---

## 🏆 CÁCH 1 (Khuyên Dùng Nhất): Dùng Cloudflare Tunnel (Miễn Phí 100%, Không Cần Tài Khoản)

**Cloudflare Tunnel (`cloudflared`)** là giải pháp tốt nhất hiện nay:
- ✅ Hoàn toàn miễn phí, không giới hạn thời gian hay số lượng thiết bị truy cập.
- ✅ Cấp sẵn tên miền **HTTPS** bảo mật chuẩn quốc tế.
- ✅ **Không cần đăng ký tài khoản**, không cần mở port modem.
- ✅ 10, 50 hay 100 điện thoại truy cập cùng một lúc vẫn mượt mà.

### Các bước thực hiện:

#### Bước 1: Cài đặt Cloudflared (Chỉ làm 1 lần)
Mở **PowerShell** trên máy tính và chạy lệnh:
```powershell
winget install --id Cloudflare.cloudflared
```
*(Hoặc tải file `cloudflared-windows-amd64.exe` trực tiếp từ trang chính thức của Cloudflare và đổi tên thành `cloudflared.exe` bỏ vào thư mục dự án).*

#### Bước 2: Bật Tunnel chia sẻ ứng dụng
Sau khi đã bật Backend và Frontend trên máy, mở terminal mới và chạy:
```powershell
cloudflared tunnel --url http://localhost:5173
```
*(Hoặc chỉ cần nhấp đúp chuột vào file `start_public_tunnel.bat` có sẵn trong thư mục dự án).*

#### Bước 3: Lấy link gửi cho điện thoại
Trên màn hình console sẽ hiện ra đường link dạng:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://ancient-sample-voices.trycloudflare.com                                           |
+--------------------------------------------------------------------------------------------+
```

👉 **Gửi link `https://xxxx.trycloudflare.com` này cho bất kỳ ai!**
- Điện thoại dùng 4G, 5G hay WiFi bất kỳ đều mở được ngay.
- Trình duyệt sẽ hỏi: *"Cho phép trang web sử dụng Camera?"* → Chọn **Cho phép (Allow)**.
- Đưa camera lên quét mã QR tại hiện vật (hoặc trên màn hình máy tính) để nghe thuyết minh!

---

## ⚡ CÁCH 2: Dùng LocalTunnel (Có Sẵn Node.js, Không Cần Cài Thêm Gì)

Vì máy tính bạn đã cài sẵn Node.js (`npx`), bạn có thể dùng ngay công cụ này:

### Các bước thực hiện:
Mở terminal trên máy tính và gõ:
```bash
npx localtunnel --port 5173
```

Màn hình sẽ hiển thị:
```
your url is: https://bright-tiger-42.loca.lt
```

### Cách mở trên điện thoại:
1. Mở link `https://xxxx.loca.lt` trên trình duyệt điện thoại.
2. Lần đầu tiên mở, LocalTunnel sẽ yêu cầu xác nhận một mã **Tunnel Password**.
3. Để lấy mã này:
   - Trên máy tính, mở trang: `https://loca.lt/mytunnelpassword`
   - Copy dãy số IP hiện ra (ví dụ: `113.161.45.22`).
   - Dán số này vào ô trên điện thoại và bấm **Submit**.
4. Toàn bộ giao diện WarRemnantsVoice sẽ hiện ra và sử dụng bình thường.

---

## 🔒 CÁCH 3: Dùng Ngrok

Nếu bạn đã quen thuộc với Ngrok:
```bash
ngrok http 5173
```
Ngrok sẽ cung cấp đường link HTTPS (ví dụ: `https://abc-123.ngrok-free.app`). Chia sẻ link này cho các điện thoại cùng truy cập.

---

## 📶 CÁCH 4: Truy Cập Khi Chung Mạng WiFi (Mạng Nội Bộ LAN)

Nếu tất cả các thiết bị cùng kết nối vào 1 mạng WiFi (ví dụ WiFi văn phòng, bảo tàng, hoặc nhà):

1. Mở PowerShell trên máy tính gõ: `ipconfig`
2. Tìm dòng `IPv4 Address`, ví dụ: `192.168.1.50`
3. Trên điện thoại mở:
   - `http://192.168.1.50:5173`
4. *Lưu ý về Camera khi dùng HTTP nội bộ:*
   - Trên Google Chrome Android: Nếu camera bị chặn do không có HTTPS, vào `chrome://flags` trên điện thoại → Tìm `unsafely-treat-insecure-origin-as-secure` → Nhập `http://192.168.1.50:5173` → Chọn **Enable** → Bấm **Relaunch**.
   - Hoặc đơn giản là dùng tính năng **"Tải ảnh mã QR"** có sẵn trên giao diện.

---

## 🎯 Tổng Kết Quy Trình Chạy Cho Buổi Demo / Thuyết Trình

Khi cần demo cho nhiều người cùng trải nghiệm trên điện thoại:

1. **Khởi động Backend:** Chạy `start_backend.bat` (Cửa sổ 1).
2. **Khởi động Frontend:** Chạy `start_frontend.bat` (Cửa sổ 2).
3. **Mở Chia Sẻ Public:** Chạy `start_public_tunnel.bat` (Cửa sổ 3).
4. Copy đường link HTTPS tạo được (ví dụ `https://xxx.trycloudflare.com`) gửi vào Zalo / Messenger cho mọi người.
5. Mở trang `http://localhost:5173/qr-codes` trên màn hình máy tính / máy chiếu để hiển thị các bảng mã QR hiện vật mẫu.
6. Mọi người cầm điện thoại lên, mở link, cấp quyền camera và quét trực tiếp lên màn hình máy chiếu!
