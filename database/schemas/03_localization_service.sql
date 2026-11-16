-- ============================================================================
-- LOCALIZATION & GLOSSARY SERVICE SCHEMA (localization_db / localization_service)
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Bounded Context: Quản lý bản dịch 15+ ngôn ngữ, mốc thời gian phụ đề & từ điển thuật ngữ lịch sử
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS localization_service;

SET search_path TO localization_service, public;

-- ----------------------------------------------------------------------------
-- 1. BẢNG TỪ ĐIỂN CHUẨN HÓA THUẬT NGỮ LỊCH SỬ - QUÂN SỰ (glossary)
-- Ràng buộc bắt buộc tuân thủ cho Translation Worker (BR-02, FR-11)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS localization_service.glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term_vi VARCHAR(150) UNIQUE NOT NULL,                   -- Thuật ngữ, tên riêng, địa danh lịch sử tiếng Việt nguồn
    term_en VARCHAR(150) NOT NULL,                          -- Bản dịch tiếng Anh chuẩn hội đồng bảo tàng phê duyệt
    context_note VARCHAR(255),                              -- Ghi chú ngữ cảnh (VD: Tên chiến dịch năm 1972, không dịch nghĩa đen)
    is_restricted BOOLEAN NOT NULL DEFAULT TRUE,            -- Cờ bắt buộc AI phải tuân thủ nghiêm ngặt theo từ điển
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE localization_service.glossary IS 'Bộ từ điển thuật ngữ lịch sử quân sự bắt buộc áp dụng khi dịch máy';
COMMENT ON COLUMN localization_service.glossary.term_vi IS 'Thuật ngữ tiếng Việt gốc (Unique)';
COMMENT ON COLUMN localization_service.glossary.is_restricted IS 'Nếu TRUE, prompt LLM bắt buộc thay thế chính xác thuật ngữ này';

-- ----------------------------------------------------------------------------
-- 2. BẢNG BẢN DỊCH VÀ MỐC THỜI GIAN PHỤ ĐỀ ĐA NGÔN NGỮ (localization)
-- Lưu trữ bản dịch 15+ thứ tiếng và mốc thời gian JSON cuộn phụ đề theo giọng đọc
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS localization_service.localization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL,                               -- Tham chiếu logic sang Exhibit Core Service (Khử khóa ngoại cứng)
    language_code VARCHAR(10) NOT NULL,                     -- Mã ngôn ngữ quốc tế (en, fr, zh, ja, es, de, ko, ru...)
    translated_title VARCHAR(255) NOT NULL,                 -- Tiêu đề hiện vật đã dịch
    translated_text TEXT NOT NULL,                          -- Toàn bộ nội dung thuyết minh đã dịch
    timestamps_json JSONB,                                  -- Mốc thời gian từng câu: [{"start_ms": 0, "end_ms": 2500, "text": "..."}]
    content_version INT NOT NULL,                           -- Khớp với content_version của hiện vật nguồn
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,             -- Đã được cán bộ bảo tàng kiểm duyệt và phê duyệt (BR-13)
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- RÀNG BUỘC UQ1: Mỗi hiện vật tại 1 phiên bản chỉ có DUY NHẤT 1 bản dịch cho mỗi ngôn ngữ
    CONSTRAINT uq_localization_exhibit_lang_version UNIQUE (exhibit_id, language_code, content_version)
);

COMMENT ON TABLE localization_service.localization IS 'Bản dịch đa ngôn ngữ và siêu dữ liệu mốc thời gian phụ đề';
COMMENT ON COLUMN localization_service.localization.exhibit_id IS 'Khóa ngoại logic liên kết sang bảng exhibit trong exhibit_service';
COMMENT ON COLUMN localization_service.localization.timestamps_json IS 'Dữ liệu JSON định vị thời gian khớp giọng đọc phục vụ cuộn phụ đề';
COMMENT ON COLUMN localization_service.localization.is_reviewed IS 'Cờ biên tập viên phê duyệt trước khi xuất bản ra ứng dụng khách';

-- ----------------------------------------------------------------------------
-- CHỈ MỤC TỐI ƯU HÓA HIỆU NĂNG (INDEXES)
-- ----------------------------------------------------------------------------
-- Tra cứu bản dịch phục vụ khách tham quan: Cực nhanh theo exhibit_id, ngôn ngữ và phiên bản mới nhất
CREATE INDEX IF NOT EXISTS idx_localization_lookup 
ON localization_service.localization(exhibit_id, language_code, content_version DESC);

-- Lọc danh sách bản dịch cần biên tập viên kiểm duyệt
CREATE INDEX IF NOT EXISTS idx_localization_review_status 
ON localization_service.localization(is_reviewed, language_code);

-- Tìm kiếm nhanh thuật ngữ tiếng Việt trong Glossary
CREATE INDEX IF NOT EXISTS idx_glossary_term_vi 
ON localization_service.glossary(term_vi);

-- ----------------------------------------------------------------------------
-- TRIGGER CẬP NHẬT THỜI GIAN
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION localization_service.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_localization_updated_at ON localization_service.localization;
CREATE TRIGGER trg_localization_updated_at
BEFORE UPDATE ON localization_service.localization
FOR EACH ROW EXECUTE FUNCTION localization_service.update_updated_at_column();
