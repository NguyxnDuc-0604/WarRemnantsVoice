# 🎖️ WarRemnantsVoice — Smart Audio Guide & PWA CMS
### Bảo Tàng Chứng Tích Chiến Tranh TP. Hồ Chí Minh (War Remnants Museum)

Hệ thống thuyết minh tự động đa ngôn ngữ cho bảo tàng ứng dụng kiến trúc **Microservices**, **AI Speech Synthesis (TTS)** và **Web Audio Streaming**. Khách tham quan không cần tải ứng dụng, chỉ cần dùng camera điện thoại quét mã QR tại hiện vật để thưởng thức nội dung thuyết minh đồng bộ phụ đề theo thời gian thực.

---

## 🏛️ Kiến Trúc Hệ Thống (Microservices Architecture)

```
                              [ Du khách / Trình duyệt PWA ]
                                            │
                                            ▼
                           ┌─────────────────────────────────┐
                           │   API Gateway (Port 8000)       │
                           │   (Reverse Proxy / Load Router) │
                           └───────────────┬─────────────────┘
                                           │
         ┌──────────────────┬──────────────┴─────┬──────────────────┐
         ▼                  ▼                    ▼                  ▼
┌──────────────────┐ ┌───────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ Exhibit Service  │ │ Analytics     │ │ AI Pipeline       │ │ Streaming         │
│ (Port 8001)      │ │ Service (8002)│ │ Service (8003)    │ │ Service (8004)    │
│ CRUD, Tours      │ │ CCU, Metrics  │ │ TTS & Translation │ │ HTTP 206 Partial  │
└────────┬─────────┘ └───────┬───────┘ └───────────────────┘ └─────────┬─────────┘
         │                   │                                         │
         ▼                   ▼                                         ▼
┌────────────────────────────────────┐                        ┌──────────────────┐
│   PostgreSQL 16 (Port 5432)        │                        │ MinIO Storage    │
│   (Database per Service Isolation) │                        │ (Audio Objects)  │
└────────────────────────────────────┘                        └──────────────────┘
```

---

## 📂 Tổ Chức Thư Mục Dự Án (Directory Structure)

```
war-remnants-voice/
├── .github/                      # CI/CD Workflows (GitHub Actions)
│   └── workflows/
│       ├── ci.yml                # Continuous Integration (syntax & test)
│       └── cd.yml                # Continuous Deployment (Matrix Build & Rolling Update)
│
├── database/                     # Thiết kế cơ sở dữ liệu
│   ├── schemas/                  # Schema phân tách theo từng Service
│   ├── seeds/                    # Dữ liệu hiện vật mẫu chuẩn PRD
│   └── init_database.sql         # Script khởi tạo tự động cho PostgreSQL
│
├── docs/                         # Tài liệu kỹ thuật
│   ├── MICROSERVICES_ARCHITECTURE.md # Báo cáo kiến trúc Microservices chi tiết
│   ├── api-contracts.md          # OpenAPI / Swagger Contracts
│   └── diagrams.md               # Sơ đồ C4 & Flowcharts
│
├── scripts/                      # Công cụ & Tiện ích phát triển
│   ├── xem_database.bat          # Kiểm tra nhanh các bảng SQLite
│   ├── truy_van_sql.bat          # CLI truy vấn SQL tương tác
│   ├── start_tunnel.ps1          # Tạo tunnel Cloudflare cho điện thoại 4G/5G
│   └── archive/                  # Lưu trữ mã nguồn nguyên mẫu cũ (Celery)
│
├── services/                     # 6 Microservices độc lập
│   ├── gateway-service/          # Cổng API Gateway tập trung (Port 8000)
│   ├── exhibit-service/          # Quản lý hiện vật & tour (Port 8001)
│   ├── analytics-service/        # Thống kê CCU & lượt nghe (Port 8002)
│   ├── ai-pipeline-service/      # AI TTS & đa ngôn ngữ (Port 8003)
│   ├── streaming-service/        # Phát audio từng phần HTTP 206 (Port 8004)
│   └── frontend/                 # Giao diện PWA React + Vite (Port 5173)
│
├── docker-compose.yml            # Khởi chạy toàn bộ hệ thống bằng Docker
├── start_all_microservices.bat   # 1-Click khởi động tất cả microservices
├── stop_all_microservices.bat    # 1-Click dừng toàn bộ hệ thống
├── start_public_tunnel.bat       # Mở link công khai ra Internet cho khách
└── README_CHAY_DU_AN.md          # Hướng dẫn chi tiết vận hành & kiểm thử
```

---

## 🚀 Hướng Dẫn Khởi Động

### Cách 1: Chạy chuẩn Microservices với Docker (Khuyến nghị)

Yêu cầu: Đã cài đặt [Docker Desktop](https://www.docker.com/).

```bash
# 1. Khởi động toàn bộ cụm Microservices
docker compose up -d --build

# Hoặc nhấp đúp file:
# start_all_microservices.bat
```

Sau khi khởi động:
- **Trang chủ du khách (PWA):** `http://localhost:5173`
- **Trang quản trị (Admin CMS):** `http://localhost:5173/admin`
- **Biển quét mã QR:** `http://localhost:5173/qr-stands`
- **Kiểm tra trạng thái cụm:** `http://localhost:8000/health`

### Cách 2: Chạy cục bộ bằng Batch Script (Dành cho máy không có Docker)

1. Nhấp đúp `start_backend.bat` (Khởi chạy FastAPI tại port 8000).
2. Nhấp đúp `start_frontend.bat` (Khởi chạy React Vite tại port 5173).

---

## 📱 Kiểm Thử Bằng Điện Thoại Ngoài Internet (4G/5G)

1. Nhấp đúp `start_public_tunnel.bat`.
2. Lấy link `https://*.trycloudflare.com` hiển thị trên màn hình.
3. Mở `http://localhost:5173/qr-stands` trên máy tính, dán link tunnel vào.
4. Dùng điện thoại (Camera iPhone/Android hoặc Zalo) quét mã QR để nghe thuyết minh trực tiếp.

---

## 👥 Nhóm Thực Hiện
- **Dự án:** WarRemnantsVoice — Smart Audio Guide
- **Đối tượng:** Bảo tàng Chứng tích Chiến tranh TP. Hồ Chí Minh
- **Phiên bản:** MVP v1.0
