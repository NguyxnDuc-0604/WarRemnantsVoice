# 🤖 Báo Cáo Kỹ Thuật: Thành Viên 2 — AI & Pipeline Processing Services
### Dự án: WarRemnantsVoice (Bảo tàng Chứng tích Chiến tranh)

---

## 🎯 I. PHẠM VI CÔNG VIỆC CỦA THÀNH VIÊN 2 (ROLE RESPONSIBILITIES)

Theo phân công đồ án kỹ thuật phần mềm, **Thành viên 2** chịu trách nhiệm toàn diện về phân hệ trí tuệ nhân tạo (AI Pipeline) và xử lý dữ liệu âm thanh/dịch thuật:

1. **ASR & NLP Service (Python):**
   - Bóc tách giọng nói từ tệp ghi âm của thuyết minh viên thành văn bản tiếng Việt.
   - NLP Module chuẩn hóa chính tả, căn chỉnh dấu câu và định dạng câu từ.
2. **Translation & Localization Service (Python):**
   - Tự động dịch văn bản thuyết minh sang 15 ngôn ngữ đích.
   - Áp dụng chuẩn từ điển thuật ngữ lịch sử - quân sự (**Historical Glossary**) để đảm bảo tính tôn nghiêm và chính xác (ví dụ: *Ấp Bắc* $\rightarrow$ *Ap Bac*, *Chiến dịch Hồ Chí Minh* $\rightarrow$ *Ho Chi Minh Campaign*).
3. **TTS Service (Python):**
   - Chuyển đổi văn bản đa ngôn ngữ thành tệp âm thanh MP3 truyền cảm bằng mô hình Neural Voice (Microsoft Edge TTS).
   - Tự động tính toán và sinh chuỗi **Timestamps phụ đề đồng bộ (Subtitle Sync)** theo từng câu đọc.
4. **Task Worker & Message Queue:**
   - Điều phối xử lý bất đồng bộ các yêu cầu tạo thuyết minh thông qua RabbitMQ và bảng `pipeline_job`.
5. **Kiến Trúc Database-per-Service (Microservices Isolation):**
   - Tách biệt cơ sở dữ liệu riêng `pipeline_db` (PostgreSQL / SQLite).
   - Áp dụng nguyên tắc **Decoupled Logical Foreign Keys** kết nối với `exhibit_db` và `gateway_db`.
6. **Hạ Tầng & CI/CD:**
   - Tối ưu hóa Dockerfile đa tầng (Multi-stage build) giúp giảm kích thước container image.
   - Viết trọn bộ 20 Unit Tests tự động và cấu hình GitHub Actions CI pipeline.

---

## 🗄️ II. THIẾT KẾ DATABASE-PER-SERVICE (PIPELINE_DB)

Trong mô hình Microservices, `ai-pipeline-service` độc lập hoàn toàn với `exhibit_db`:

```
┌─────────────────────────────────────────────────────────────┐
│                       pipeline_db                           │
│  (Sở hữu độc quyền bởi AI Pipeline & Localization Service)  │
├──────────────────────┬──────────────────────────────────────┤
│ Bảng                 │ Mô tả                                │
├──────────────────────┼──────────────────────────────────────┤
│ supported_language   │ Danh mục 15 ngôn ngữ & voice model   │
│ glossary             │ Từ điển chuẩn hóa thuật ngữ lịch sử  │
│ localization         │ Bản dịch đa ngôn ngữ + timestamps    │
│ audio_media          │ Tệp âm thanh thuyết minh AI          │
│ pipeline_job         │ Quản lý tiến trình xử lý hàng đợi    │
└──────────────────────┴──────────────────────────────────────┘
```

### 🔗 Nguyên tắc Decoupled Logical Foreign Key
Bảng `localization` và `pipeline_job` **không sử dụng ràng buộc khóa ngoại cứng** (`REFERENCES exhibit(id)`), mà chỉ lưu trữ:
- `exhibit_id`: Chuỗi UUID định danh hiện vật từ Exhibit Service.
- `exhibit_code`: Mã hiện vật (ví dụ: `UH1-BELL`, `T54-390`).

Nhờ đó, khi `exhibit-service` nâng cấp hoặc bảo trì, `ai-pipeline-service` vẫn hoạt động độc lập mà không bị lỗi ràng buộc dữ liệu toàn vẹn giữa các schema.

---

## 🚀 III. DANH SÁCH API ENDPOINTS ĐÃ TRIỂN KHAI

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/` | Healthcheck & kiểm tra trạng thái kết nối `pipeline_db` |
| `GET` | `/api/v1/languages` | Danh mục 15 ngôn ngữ khả dụng |
| `GET` | `/api/v1/glossary` | Từ điển chuẩn hóa thuật ngữ lịch sử |
| `POST` | `/api/v1/ai/nlp/normalize` | Chuẩn hóa chính tả và ngữ pháp NLP |
| `POST` | `/api/v1/process-audio` | Pipeline dịch thuật & sinh audio TTS đồng bộ |
| `POST` | `/api/v1/pipeline/jobs` | Đưa yêu cầu sinh audio vào hàng đợi bất đồng bộ |
| `GET` | `/api/v1/pipeline/jobs` | Danh sách lịch sử các jobs trong hệ thống |
| `GET` | `/api/v1/pipeline/jobs/{id}` | Tra cứu trạng thái chi tiết của 1 job |

---

## ✅ IV. BỘ KIỂM THỬ TỰ ĐỘNG (20 UNIT TESTS)

Toàn bộ 20 Unit Tests kiểm thử tự động (pytest) đã vượt qua 100%:
1. `tests/test_translation.py` (5 tests): Dịch thuật, fallback, glossary thay thế thuật ngữ lịch sử.
2. `tests/test_tts.py` (3 tests): Voice mapping 15 thứ tiếng, thuật toán sinh phụ đề timestamps.
3. `tests/test_asr_nlp.py` (4 tests): Chuẩn hóa khoảng trắng, viết hoa, dấu câu, bắt lỗi tệp âm thanh.
4. `tests/test_pipeline_db.py` (3 tests): Khởi tạo schema `pipeline_db`, kiểm tra Decoupled FK, vòng đời PipelineJob.
5. `tests/test_api_endpoints.py` (5 tests): Healthcheck, languages, glossary, NLP endpoint, Pipeline Jobs API.

---

*Tài liệu kỹ thuật lập bởi Thành viên 2 — Đồ án Công Nghệ Phần Mềm WarRemnantsVoice*
