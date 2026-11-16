# CƠ SỞ DỮ LIỆU HỆ THỐNG THUYẾT MINH TỰ ĐỘNG ĐA NGÔN NGỮ
## BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH (WarRemnantsVoice)

Tài liệu hướng dẫn kiến trúc, thiết kế chi tiết và vận hành cơ sở dữ liệu cho dự án **WarRemnantsVoice** theo đúng chuẩn mực Product Requirements Document (PRD v1.0 - Tháng 10/2026).

---

## 1. Cấu trúc Thư mục Cơ sở Dữ liệu

```
WarRemnantsVoice/database/
├── README.md                      # Tài liệu thuyết minh CSDL & Hướng dẫn sử dụng
├── schema_all_in_one.sql          # Master script SQL khởi tạo toàn bộ CSDL và dữ liệu mẫu trên 1 Postgres instance
├── init_microservices_db.sql      # Script tạo 5 CSDL độc lập (Database-per-Service)
├── docker-compose.db.yml          # Docker Compose: PostgreSQL 16, pgAdmin4, Redis, MinIO, RabbitMQ
├── test_db_sqlite.py              # Script Python kiểm thử nhanh nghiệp vụ (không cần cài đặt PostgreSQL)
├── war_remnants_test.db           # CSDL SQLite kiểm thử độc lập
├── schemas/                       # DDL phân tách theo Bounded Context của từng Microservice
│   ├── 01_auth_service.sql        # Phân hệ Auth: system_user, system_role, system_permission, audit_log
│   ├── 02_exhibit_service.sql     # Phân hệ Exhibit: exhibit, content_source, tour_route, outbox_event
│   ├── 03_localization_service.sql# Phân hệ Localization: localization, glossary
│   ├── 04_media_service.sql       # Phân hệ Streaming/Media: audio_media
│   └── 05_metric_service.sql      # Phân hệ Analytics: listening_metric, views
└── seeds/
    └── 06_seed_data.sql           # Dữ liệu mẫu chuẩn lịch sử bảo tàng (T-54, C-130, UH-1, Máy chém, Dioxin...)
```

---

## 2. Bounded Context & Phân bổ Bảng theo Microservices

Hệ thống tuân thủ nghiêm ngặt nguyên tắc **Database-per-Service / Logical Schemas** trên PostgreSQL:

| Tên Schema / DB | Microservice quản lý | Danh mục Bảng nghiệp vụ |
| :--- | :--- | :--- |
| `auth_service` / `auth_db` | Identity & Access Management | `system_user`, `system_role`, `system_permission`, `role_permission`, `audit_log` |
| `exhibit_service` / `exhibit_db` | Exhibit Core Service | `exhibit`, `content_source`, `tour_route`, `outbox_event` |
| `localization_service` / `localization_db` | Localization & Glossary Service | `localization`, `glossary` |
| `media_service` / `media_db` | Streaming & Media Distribution | `audio_media` (+ MinIO Buckets) |
| `metric_service` / `metric_db` | Analytics & Metric Service | `listening_metric`, `v_top_listened_exhibits`, `v_language_distribution` |

---

## 3. Đặc tả Chi tiết các Bảng Nghiệp vụ (Data Dictionary)

### 3.1. Bảng `exhibit` (Hiện vật trưng bày cốt lõi)
- `id` (UUID PK): Khóa chính duy nhất.
- `code` (VARCHAR(50) UNIQUE NOT NULL): Mã định danh nghiệp vụ mã hóa trong mã QR (VD: `T54-390`, `UH1-BELL`).
- `title` (VARCHAR(255) NOT NULL): Tên hiện vật bằng tiếng Việt chính thức.
- `room_id` (VARCHAR(50) NOT NULL): Phòng trưng bày hoặc khu vực (VD: `OUTDOOR`, `ROOM-01`).
- `latitude`, `longitude` (DECIMAL): Tọa độ GPS sân ngoài trời (VD: 10.779740, 106.692350).
- `radius` (INT DEFAULT 15): Bán kính kích hoạt Geofencing (5m – 50m).
- `thumbnail_url` (VARCHAR(500)): Link ảnh đại diện lưu trên MinIO.
- `content_version` (INT DEFAULT 1 NOT NULL): Phiên bản nội dung nguồn tiếng Việt (BR-03).
- `is_published` (BOOLEAN DEFAULT FALSE NOT NULL): Trạng thái xuất bản ra ngoài.
- `is_active` (BOOLEAN DEFAULT TRUE NOT NULL): Cờ Soft Delete (BR-12, bảo toàn toàn vẹn lịch sử).

### 3.2. Bảng `content_source` (Nội dung nguồn tiếng Việt)
- `id` (UUID PK): Khóa chính.
- `exhibit_id` (UUID FK -> exhibit(id) ON DELETE CASCADE): Hiện vật liên quan.
- `original_text` (TEXT): Văn bản tiếng Việt chuẩn do cán bộ bảo tàng nhập hoặc ASR bóc băng.
- `original_audio_url` (VARCHAR(500)): Đường dẫn file ghi âm gốc của cán bộ trên MinIO.
- `content_version` (INT NOT NULL): Phiên bản nội dung tương ứng.

### 3.3. Bảng `localization` (Bản dịch và Phụ đề đa ngôn ngữ)
- `id` (UUID PK): Khóa chính bản dịch.
- `exhibit_id` (UUID NOT NULL): **Khóa ngoại logic** trỏ sang Exhibit Service (khử FK cứng).
- `language_code` (VARCHAR(10) NOT NULL): Mã ngôn ngữ (en, fr, zh, ja, es, de, ko...).
- `translated_title` (VARCHAR(255) NOT NULL): Tiêu đề đã dịch.
- `translated_text` (TEXT NOT NULL): Nội dung thuyết minh đã dịch.
- `timestamps_json` (JSONB): Mốc thời gian từng câu `[{"start_ms": 0, "end_ms": 4200, "text": "..."}]` phục vụ cuộn phụ đề đồng bộ.
- `content_version` (INT NOT NULL): Phiên bản hiện vật mà bản dịch sinh ra từ đó.
- `is_reviewed` (BOOLEAN DEFAULT FALSE NOT NULL): Cán bộ bảo tàng đã kiểm duyệt.
- **Ràng buộc UQ1**: `UNIQUE (exhibit_id, language_code, content_version)` - chống trùng lặp job worker.

### 3.4. Bảng `audio_media` (Dữ liệu tệp âm thanh thuyết minh)
- `id` (UUID PK): Khóa chính file âm thanh.
- `localization_id` (UUID NOT NULL): **Khóa ngoại logic** trỏ sang bản dịch.
- `file_url` (VARCHAR(500) NOT NULL): Đường dẫn phát audio trực tiếp (HTTP Range).
- `storage_path` (VARCHAR(255) NOT NULL): Object key trên MinIO (`audio-media/exhibits/...`).
- `duration_seconds` (DECIMAL(8, 2) NOT NULL): Tổng thời lượng bài nghe.
- `bitrate_kbps` (INT DEFAULT 128): Bitrate chuẩn 128 kbps.
- `voice_code` (VARCHAR(50)): Mã giọng đọc Neural TTS (VD: `en-US-GuyNeural`, `fr-FR-HenriNeural`).
- `status` (VARCHAR(20) NOT NULL DEFAULT 'ready'): `pending`, `processing`, `ready`, `failed`.

### 3.5. Bảng `tour_route` (Lộ trình chuyên đề)
- `id` (UUID PK): Khóa chính lộ trình.
- `title` (VARCHAR(255) NOT NULL): Tên lộ trình (VD: "Khí tài Quân sự Ngoài trời").
- `description` (TEXT): Ý nghĩa, bối cảnh lịch sử tuyến tham quan.
- `ordered_exhibits_json` (JSONB NOT NULL): Mảng UUID các hiện vật theo thứ tự ghé thăm khuyến nghị.
- `estimated_time` (INT NOT NULL): Thời gian hoàn thành (phút).
- `is_active` (BOOLEAN DEFAULT TRUE NOT NULL): Trạng thái kích hoạt.

### 3.6. Bảng `glossary` (Từ điển chuẩn hóa thuật ngữ lịch sử)
- `id` (UUID PK): Khóa chính từ điển.
- `term_vi` (VARCHAR(150) UNIQUE NOT NULL): Thuật ngữ, địa danh, tên riêng tiếng Việt gốc.
- `term_en` (VARCHAR(150) NOT NULL): Bản dịch tiếng Anh chuẩn đã kiểm định.
- `context_note` (VARCHAR(255)): Hướng dẫn ngữ cảnh (VD: "Tên chiến dịch, không dịch nghĩa đen").
- `is_restricted` (BOOLEAN DEFAULT TRUE NOT NULL): Bắt buộc AI dịch thuật phải tuân thủ nghiêm ngặt (BR-02).

### 3.7. Bảng `listening_metric` (Thống kê lượt nghe ẩn danh)
- `id` (BIGSERIAL PK): Khóa chính tự tăng tối ưu dữ liệu chuỗi thời gian.
- `exhibit_id` (UUID NOT NULL): Hiện vật được nghe.
- `language_code` (VARCHAR(10) NOT NULL): Ngôn ngữ khách đã nghe.
- `listened_duration` (INT NOT NULL): Thời lượng thực tế đã nghe (giây).
- `trigger_type` (VARCHAR(20) NOT NULL): `QR_CODE` hoặc `GPS_GEOFENCE`.
- `timestamp` (TIMESTAMPTZ DEFAULT NOW()): Thời điểm nghe (tuyệt đối không lưu IP hay thông tin cá nhân - BR-15).

---

## 4. Các Ràng buộc Kiến trúc Phân tán Nâng cao

1. **Khử khóa ngoại cứng (Decoupled Logical Foreign Keys):**
   - Giữa các dịch vụ (ví dụ: `localization.exhibit_id`, `audio_media.localization_id`, `listening_metric.exhibit_id`), hệ thống lưu trữ kiểu `UUID` logic nhưng **không tạo câu lệnh `REFERENCES` ở cấp độ RDBMS**.
   - Điều này cho phép các microservice deploy độc lập và chia tách database mà không bao giờ bị ràng buộc khóa ngoại chéo.

2. **Transactional Outbox Pattern (Eventual Consistency):**
   - Khi cán bộ sửa nội dung gốc tiếng Việt, Exhibit Core Service cập nhật `content_source` và ghi sự kiện vào bảng `outbox_event` trong cùng 1 Database Transaction.
   - Tiến trình Message Relay đọc các sự kiện chưa xử lý (`processed = FALSE`) và đẩy vào RabbitMQ để Localization Service và Streaming Service vô hiệu hóa các bản dịch cũ và tạo mới.

3. **Soft Delete (`is_active`):**
   - Cấm dùng lệnh `DELETE` vật lý đối với `exhibit`. Chỉ cập nhật `is_active = FALSE` để bảo toàn tính toàn vẹn cho các báo cáo lịch sử trong `listening_metric`.

---

## 5. Hướng dẫn Khởi chạy và Kiểm thử

### Cách 1: Kiểm thử Nhanh với Python & SQLite (Khuyến nghị khi chưa cài PostgreSQL/Docker)
Script đã được cấu hình sẵn mọi bảng và chèn dữ liệu mẫu chuẩn của Bảo tàng Chứng tích Chiến tranh:
```powershell
python database/test_db_sqlite.py
```
*Kết quả sẽ chạy 5 test case nghiệp vụ:*
1. Quét QR Code `T54-390` $\rightarrow$ Lấy hiện vật, phụ đề tiếng Anh và URL audio streaming.
2. Định vị GPS sân ngoài trời (Haversine Formula) $\rightarrow$ Tự động nhận diện Xe tăng T-54 số 390.
3. Duyệt tuyến tham quan chuyên đề $\rightarrow$ Duyệt mảng `ordered_exhibits_json`.
4. Ràng buộc từ điển `Glossary` $\rightarrow$ Áp đặt danh từ riêng quân sự.
5. Dashboard Observability $\rightarrow$ Thống kê Top hiện vật và tỷ lệ ngôn ngữ du khách.

### Cách 2: Triển khai Cụm Dữ liệu Toàn diện với Docker Compose
Khởi chạy PostgreSQL 16, pgAdmin4, Redis Cache, MinIO Object Storage và RabbitMQ:
```bash
docker compose -f database/docker-compose.db.yml up -d
```
- **PostgreSQL:** `localhost:5432` (User: `postgres`, Password: `postgres123`, DB: `warremnants_db`)
- **pgAdmin 4 Web UI:** `http://localhost:5050` (Tài khoản: `admin@baotang.vn` / `admin123`)
- **MinIO Console:** `http://localhost:9001` (`minioadmin` / `minioadmin123`)
- **RabbitMQ Management:** `http://localhost:15672` (`guest` / `guest`)

### Cách 3: Nạp thủ công vào PostgreSQL sẵn có
Chạy master script tổng hợp:
```bash
psql -U postgres -d warremnants_db -f database/schema_all_in_one.sql
```
