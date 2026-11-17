# 🛠️ Thư Mục Công Cụ & Scripts — WarRemnantsVoice

Thư mục này chứa các tiện ích phục vụ phát triển cục bộ (Local Development), kiểm tra cơ sở dữ liệu và công cụ tạo đường hầm kết nối (Tunneling).

---

## 📋 Danh sách công cụ

| Tập tin | Loại | Mô tả công dụng |
|---------|------|-----------------|
| `xem_database.bat` | Batch Script | Click đúp để xem toàn bộ bảng và dữ liệu mẫu trong CSDL SQLite cục bộ (theo chuẩn PRD Part III). |
| `show_database.py` | Python Script | Script Python đọc và in toàn bộ schema & dữ liệu mẫu ra terminal định dạng bảng đẹp mắt. |
| `truy_van_sql.bat` | Batch Script | Mở giao diện dòng lệnh (CLI) tương tác trực tiếp bằng SQL với CSDL. |
| `truy_van_sql.py` | Python Script | Interactive SQL Runner hỗ trợ các truy vấn mẫu như xem danh sách hiện vật, từ điển lịch sử, v.v. |
| `start_tunnel.ps1` | PowerShell | Khởi tạo Cloudflare Tunnel ngầm, tự động bắt URL `https://*.trycloudflare.com` và hiển thị mã QR ra màn hình để quét bằng điện thoại. |

---

## 🗄️ Thư mục lưu trữ (Archive)

- `archive/legacy_celery_worker/`: Chứa mã nguồn thử nghiệm ban đầu dùng Celery + Redis + Whisper (trước khi chuyển đổi sang kiến trúc Microservices FastAPI độc lập). Được lưu lại để đối chiếu lịch sử phát triển.
