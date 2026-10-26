# 🎖️ WarRemnantsVoice — Hướng Dẫn Chạy Dự Án & Quét Mã QR

Hệ thống AI Audio Guide thuyết minh đa ngôn ngữ tự động (13+ ngôn ngữ) cho **Bảo tàng Chứng tích Chiến tranh TP. Hồ Chí Minh** kết hợp tính năng **Quét Mã QR hiện vật trực tiếp bằng camera điện thoại**.

---

## 📁 Cấu Trúc Dự Án

```
war-remnants-voice/
├── start_backend.bat            ← Khởi động Backend 1-click
├── start_frontend.bat           ← Khởi động Frontend 1-click
├── start_public_tunnel.bat      ← Mở link HTTPS chia sẻ cho điện thoại 4G/5G
├── HUONG_DAN_TRUY_CAP_TU_XA.md  ← Chi tiết cách truy cập không chung mạng
│
├── services/
│   ├── ai-pipeline-service/     ← Backend Python FastAPI
│   │   ├── app/
│   │   │   ├── services/
│   │   │   │   ├── translate_service.py  ← Google Translate + Glossary
│   │   │   │   └── tts_service.py        ← Microsoft Edge TTS Neural (13 giọng)
│   │   │   └── utils/glossary.py         ← Thuật ngữ lịch sử chuẩn hoá
│   │   ├── output/                       ← File MP3 thuyết minh tự sinh
│   │   ├── main_fastapi.py              ← FastAPI server + Exhibit API
│   │   └── requirements.txt
│   │
│   └── frontend/                ← Frontend React 18 + Vite (Mobile-First)
│       ├── src/
│       │   ├── pages/
│       │   │   ├── HomePage.jsx          ← Trang chủ giới thiệu
│       │   │   ├── QRScanPage.jsx        ← Quét mã QR hiện vật & nghe audio
│       │   │   ├── TranslatePage.jsx     ← Nhập văn bản thuyết minh tự do
│       │   │   └── QRExhibitsPage.jsx    ← Thư viện mã QR mẫu để test
│       │   ├── components/
│       │   │   ├── QRScanner.jsx         ← Khung quét QR laser + camera switcher
│       │   │   ├── AudioPlayer.jsx       ← Trình phát âm thanh tùy chỉnh cao cấp
│       │   │   ├── LanguageSelector.jsx  ← Chọn 13 ngôn ngữ kèm cờ quốc gia
│       │   │   ├── TranslationCard.jsx   ← Thẻ kết quả dịch & âm thanh
│       │   │   └── Header.jsx            ← Navigation bar tối ưu mobile
│       │   └── api/pipelineApi.js
│       └── package.json
```

---

## 🚀 CÁCH KHỞI ĐỘNG DỰ ÁN

### Cách 1: Chạy Siêu Tốc Bằng File `.bat` (Khuyên dùng trên Windows)
1. Nhấp đúp chuột vào `start_backend.bat` (Cửa sổ 1 - Backend FastAPI).
2. Nhấp đúp chuột vào `start_frontend.bat` (Cửa sổ 2 - Frontend React Vite).
3. Mở trình duyệt máy tính vào: `http://localhost:5173`

---

### Cách 2: Chạy Thủ Công Bằng Terminal

#### Cửa sổ 1: Khởi động Backend (FastAPI - Port 8000)
```powershell
cd "d:\VS Code\war-remnants-voice\services\ai-pipeline-service"

# Kích hoạt môi trường ảo (nếu có)
.\venv\Scripts\activate

# Cài đặt thư viện (nếu chưa cài)
pip install -r requirements.txt

# Khởi động server
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
```
✅ Khi thấy: `Uvicorn running on http://0.0.0.0:8000` là thành công.

#### Cửa sổ 2: Khởi động Frontend (React - Port 5173)
```powershell
cd "d:\VS Code\war-remnants-voice\services\frontend"

# Cài đặt thư viện (nếu chưa cài)
npm install

# Khởi động server
npm run dev
```
✅ Khi thấy: `Local: http://localhost:5173/` là thành công.

---

## 📱 TRUY CẬP TỪ NHIỀU ĐIỆN THOẠI CÙNG LÚC (KHÔNG CHUNG MẠNG)

> **Tại sao cần Tunnel HTTPS?**
> Trình duyệt điện thoại (Safari trên iPhone, Chrome trên Android) **bắt buộc phải có kết nối HTTPS** mới cho phép mở **Camera quét mã QR**. 
> Khi dùng các công cụ Tunnel dưới đây, hệ thống sẽ tự cấp link HTTPS miễn phí cho bạn.

### Bước đơn giản nhất (Dùng Cloudflare Tunnel):
1. Nhấp đúp vào file `start_public_tunnel.bat` (hoặc mở terminal gõ: `cloudflared tunnel --url http://localhost:5173`).
2. Màn hình sẽ cung cấp một đường link HTTPS công khai (ví dụ: `https://museum-voice-example.trycloudflare.com`).
3. **Gửi link này cho bất kỳ ai!** Hàng chục điện thoại dùng mạng **4G/5G hoặc WiFi bất kỳ** đều có thể vào cùng một lúc.
4. Trên điện thoại: Chọn **Cho phép (Allow) Camera** → Hướng vào mã QR để nghe thuyết minh tức thì!

*(Xem hướng dẫn chi tiết thêm tại file [HUONG_DAN_TRUY_CAP_TU_XA.md](file:///d:/VS%20Code/war-remnants-voice/HUONG_DAN_TRUY_CAP_TU_XA.md))*

---

## 🔍 HƯỚNG DẪN TEST TÍNH NĂNG QUÉT MÃ QR HIỆN VẬT

Không cần phải in giấy ra ngoài đời thật để test, bạn có thể kiểm tra trực tiếp theo 3 cách:

### Cách 1: Test trên 2 thiết bị (Máy tính + Điện thoại)
1. Mở trang `http://localhost:5173/qr-codes` trên màn hình máy tính (Đây là **Thư viện Mã QR Hiện Vật** với các mã QR của máy bay UH-1, xe tăng M48, v.v.).
2. Cầm điện thoại mở đường link của ứng dụng (qua Cloudflare Tunnel hoặc WiFi).
3. Bấm vào nút **Quét Mã QR** trên điện thoại.
4. Hướng camera điện thoại vào mã QR trên màn hình máy tính:
   - Điện thoại sẽ phát tiếng bip nhẹ và rung.
   - Thông tin hiện vật, hình ảnh, văn bản dịch thuật và file audio thuyết minh sẽ tự động hiển thị và phát ngay!

### Cách 2: Test 1 Chạm (Mô phỏng quét nhanh trên web)
1. Truy cập trang **Quét Mã QR** (`/qr-scan`).
2. Ở cột bên trái có danh sách **"Hiện vật mẫu (Bấm để thử nghiệm ngay)"**.
3. Bấm vào bất kỳ hiện vật nào (ví dụ: *Máy bay UH-1*, *Xe tăng M48 Patton*).
4. Hệ thống sẽ tự động mô phỏng quy trình quét mã QR và tải ngay bài thuyết minh.

### Cách 3: Tải file ảnh mã QR (Upload file)
1. Trong khung quét camera, bấm vào nút **"Tải ảnh"**.
2. Chọn bất kỳ file ảnh mã QR nào được lưu trong máy để nhận diện.

---

## 🌐 13 Ngôn Ngữ Được Hỗ Trợ Với Giọng Đọc Neural Tự Nhiên

| Cờ | Mã | Ngôn ngữ | Giọng đọc Microsoft Edge TTS |
|:---:|:---:|:---|:---|
| 🇻🇳 | `vi` | Tiếng Việt | HoaiMy Neural |
| 🇬🇧 | `en` | English | Andrew Neural |
| 🇫🇷 | `fr` | Français | Henri Neural |
| 🇯🇵 | `ja` | 日本語 | Keita Neural |
| 🇰🇷 | `ko` | 한국어 | SunHi Neural |
| 🇨🇳 | `zh-CN` | 中文 (Giản thể) | Yunxi Neural |
| 🇩🇪 | `de` | Deutsch | Conrad Neural |
| 🇪🇸 | `es` | Español | Alvaro Neural |
| 🇮🇹 | `it` | Italiano | Diego Neural |
| 🇷🇺 | `ru` | Русский | Dmitry Neural |
| 🇹🇭 | `th` | ภาษาไทย | Niwat Neural |
| 🇸🇦 | `ar` | العربية | Hamed Neural |
| 🇧🇷 | `pt` | Português | Antonio Neural |

---

*WarRemnantsVoice — Bản quyền hệ thống thuộc Dự án Trợ lý Audio Guide Bảo tàng Chứng tích Chiến tranh TP.HCM*
