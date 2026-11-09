# 🗄️ Kiến Trúc Cơ Sở Dữ Liệu Microservices (Database-per-Service)
### Dự án: WarRemnantsVoice — Hệ Thống Thuyết Minh Bảo Tàng Chứng Tích Chiến Tranh

---

## 🏛️ 1. Nguyên Tắc Thiết Kế (Architectural Decisions)

Hệ thống được thiết kế theo mô hình **Microservices Database-per-Service Pattern**, tuân thủ nguyên tắc cách ly dữ liệu:
- Mỗi Microservice **sở hữu và quản lý toàn quyền một Database riêng biệt**.
- **Không thực hiện SQL JOIN liên service**: Các dịch vụ không bao giờ truy vấn trực tiếp vào database của dịch vụ khác.
- **Decoupled Logical Foreign Keys**: Mối quan hệ giữa các thực thể khác service (như `localization.exhibit_id` hoặc `listening_metric.exhibit_code`) được lưu dưới dạng chuỗi định danh (Logical FK) thay vì khóa ngoại cứng (Database Foreign Key Constraint).
- **Giao tiếp liên dịch vụ**: Thông qua RESTful API đồng bộ hoặc Message Queue (RabbitMQ / Celery) bất đồng bộ.

---

## 📊 2. Bảng Phân Bổ Database Theo Từng Service

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       HỆ THỐNG WAR REMNANTS VOICE                           │
├─────────────────────┬──────────────────┬────────────────────────────────────┤
│ Service             │ Database         │ Bảng Dữ Liệu Sở Hữu                │
├─────────────────────┼──────────────────┼────────────────────────────────────┤
│ Exhibit Service     │ exhibit_db       │ 1. exhibit                         │
│                     │ (Port 5432)      │ 2. content_source                  │
│                     │                  │ 3. tour_route                      │
├─────────────────────┼──────────────────┼────────────────────────────────────┤
│ AI Pipeline Service │ pipeline_db      │ 1. supported_language              │
│ (Thành viên 2)      │ (Port 5433)      │ 2. glossary                        │
│                     │                  │ 3. localization                    │
│                     │                  │ 4. audio_media                     │
│                     │                  │ 5. pipeline_job (Celery Worker)    │
├─────────────────────┼──────────────────┼────────────────────────────────────┤
│ Gateway & Analytics │ gateway_db       │ 1. listening_metric                │
│ Service             │ (Port 5434)      │ 2. active_session                  │
│                     │                  │ 3. visitor_log                     │
└─────────────────────┴──────────────────┴────────────────────────────────────┘
```

---

## 📁 3. Cấu Trúc Thư Mục Database

```
database/
├── schemas/
│   ├── 01_exhibit_service.sql      # DDL cho exhibit_db
│   ├── 02_pipeline_service.sql     # DDL cho pipeline_db (Thành viên 2)
│   └── 03_gateway_service.sql      # DDL cho gateway_db
├── seeds/
│   ├── 01_exhibit_seed.sql         # Seed 5 hiện vật tiêu biểu & tuyến tham quan
│   ├── 02_pipeline_seed.sql        # Seed 15 ngôn ngữ & thuật ngữ Glossary
│   └── 03_gateway_seed.sql         # Seed dữ liệu mẫu lượt nghe du khách
└── README.md                       # Tài liệu kiến trúc này
```

---

## ⚙️ 4. Cách Khởi Chạy Với Docker Compose

Khởi động toàn bộ cụm Database và Services:
```bash
docker compose up -d
```

Các Database được cấu hình tự động nạp DDL và Seed Data:
- `exhibit_db`: `postgresql://exhibit_user:exhibit_pass@localhost:5432/exhibit_db`
- `pipeline_db`: `postgresql://pipeline_user:pipeline_pass@localhost:5433/pipeline_db`
- `gateway_db`: `postgresql://gateway_user:gateway_pass@localhost:5434/gateway_db`
