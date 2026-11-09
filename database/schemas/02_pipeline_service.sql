-- ============================================================
-- pipeline_db — Database riêng cho AI Pipeline Service
-- Thành viên 2: AI & Pipeline Processing Services
-- Bảng sở hữu: supported_language, glossary, localization,
--               audio_media, pipeline_job
-- ============================================================

-- ============================================================
-- BẢNG 1: SUPPORTED_LANGUAGE
-- Danh mục 15 ngôn ngữ khả dụng, cấu hình giọng đọc TTS
-- Owned by: Translation & Localization Service
-- ============================================================
CREATE TABLE IF NOT EXISTS supported_language (
    code        VARCHAR(10) PRIMARY KEY,
    name_vi     VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag_icon   VARCHAR(10),
    voice_code  VARCHAR(50),                     -- Edge TTS voice model
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_default  BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lang_active ON supported_language(is_active, sort_order);

-- ============================================================
-- BẢNG 2: GLOSSARY
-- Từ điển chuẩn hóa thuật ngữ lịch sử - quân sự
-- Owned by: Translation Service (áp dụng sau khi dịch)
-- ============================================================
CREATE TABLE IF NOT EXISTS glossary (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term_vi      VARCHAR(150) UNIQUE NOT NULL,   -- Thuật ngữ tiếng Việt gốc
    term_en      VARCHAR(150) NOT NULL,           -- Bản dịch chuẩn tiếng Anh
    context_note VARCHAR(255),                    -- Chú thích ngữ cảnh lịch sử
    is_restricted BOOLEAN NOT NULL DEFAULT TRUE, -- Bắt buộc dùng bản dịch chuẩn
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- BẢNG 3: LOCALIZATION
-- Bản dịch đa ngôn ngữ + timestamps phụ đề đồng bộ
-- Owned by: Translation & Localization Service
-- NOTE: exhibit_id là Logical FK (không ràng buộc FOREIGN KEY thật
--       vì exhibit nằm ở exhibit_db — nguyên tắc Database-per-Service)
-- ============================================================
CREATE TABLE IF NOT EXISTS localization (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id      VARCHAR(36) NOT NULL,        -- Logical FK → exhibit_db.exhibit.id
    exhibit_code    VARCHAR(50) NOT NULL,         -- Denormalized để tra cứu nhanh
    language_code   VARCHAR(10) NOT NULL,
    translated_title VARCHAR(255) NOT NULL,
    translated_text  TEXT NOT NULL,
    timestamps_json  JSONB,                      -- Phụ đề [{id,start,end,text}]
    content_version  INT NOT NULL DEFAULT 1,
    is_reviewed     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_localization_key UNIQUE (exhibit_id, language_code, content_version)
);

CREATE INDEX IF NOT EXISTS idx_loc_exhibit    ON localization(exhibit_id, language_code);
CREATE INDEX IF NOT EXISTS idx_loc_code       ON localization(exhibit_code, language_code);
CREATE INDEX IF NOT EXISTS idx_loc_reviewed   ON localization(is_reviewed);

-- ============================================================
-- BẢNG 4: AUDIO_MEDIA
-- File âm thanh TTS đa ngôn ngữ được sinh bởi Edge TTS
-- Owned by: TTS Service
-- NOTE: localization_id là Logical FK → localization.id trong cùng DB
-- ============================================================
CREATE TABLE IF NOT EXISTS audio_media (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    localization_id  UUID NOT NULL,              -- FK trong cùng pipeline_db
    file_url         VARCHAR(500) NOT NULL,       -- URL phục vụ web (/output/...)
    storage_path     VARCHAR(255) NOT NULL,       -- Đường dẫn file trên disk
    duration_seconds DECIMAL(8, 2) NOT NULL DEFAULT 0,
    bitrate_kbps     INT DEFAULT 128,
    voice_code       VARCHAR(50),                -- Voice model đã dùng
    status           VARCHAR(20) NOT NULL DEFAULT 'ready',
    -- status: 'pending' | 'processing' | 'ready' | 'error'
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audio_localization FOREIGN KEY (localization_id)
        REFERENCES localization(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audio_loc    ON audio_media(localization_id);
CREATE INDEX IF NOT EXISTS idx_audio_status ON audio_media(status);

-- ============================================================
-- BẢNG 5: PIPELINE_JOB  (MỚI — Thêm bởi Thành viên 2)
-- Theo dõi trạng thái mỗi job xử lý pipeline (Celery Task Worker)
-- Owned by: Task Worker (RabbitMQ / Celery)
-- ============================================================
CREATE TABLE IF NOT EXISTS pipeline_job (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         VARCHAR(100) UNIQUE NOT NULL, -- Celery task UUID
    exhibit_id      VARCHAR(36) NOT NULL,          -- Logical FK → exhibit_db
    exhibit_code    VARCHAR(50) NOT NULL,
    target_languages JSONB NOT NULL DEFAULT '[]',  -- Danh sách ngôn ngữ cần xử lý
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
    priority        INT NOT NULL DEFAULT 5,         -- 1 (cao) → 10 (thấp)
    error_message   TEXT,
    retry_count     INT NOT NULL DEFAULT 0,
    max_retries     INT NOT NULL DEFAULT 3,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_exhibit ON pipeline_job(exhibit_code);
CREATE INDEX IF NOT EXISTS idx_job_status  ON pipeline_job(status);
CREATE INDEX IF NOT EXISTS idx_job_created ON pipeline_job(created_at DESC);
