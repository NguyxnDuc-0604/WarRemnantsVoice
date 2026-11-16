-- ============================================================================
-- STREAMING & MEDIA SERVICE SCHEMA (media_db / media_service)
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Bounded Context: Quản lý siêu dữ liệu tệp âm thanh thuyết minh (kết nối MinIO Object Storage)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS media_service;

SET search_path TO media_service, public;

-- ----------------------------------------------------------------------------
-- 1. BẢNG DỮ LIỆU TỆP ÂM THANH THUYẾT MINH (audio_media)
-- Lưu trữ metadata file MP3 phục vụ streaming HTTP Range Requests từ MinIO
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_service.audio_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    localization_id UUID NOT NULL,                          -- Tham chiếu logic sang Localization Service (Khử khóa ngoại cứng)
    file_url VARCHAR(500) NOT NULL,                         -- URL phát audio trực tiếp (hoặc presigned URL MinIO)
    storage_path VARCHAR(255) NOT NULL,                     -- Đường dẫn vật lý trong Bucket MinIO (VD: audio-media/exhibits/...)
    duration_seconds DECIMAL(8, 2) NOT NULL,                -- Tổng thời lượng bài thuyết minh (giây)
    bitrate_kbps INT NOT NULL DEFAULT 128,                  -- Bitrate âm thanh (mặc định 128 kbps)
    voice_code VARCHAR(50),                                 -- Mã giọng đọc AI (VD: fr-FR-HenriNeural, en-US-GuyNeural)
    status VARCHAR(20) NOT NULL DEFAULT 'ready',            -- Trạng thái: pending, processing, ready, failed
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_audio_media_duration CHECK (duration_seconds > 0),
    CONSTRAINT chk_audio_media_bitrate CHECK (bitrate_kbps >= 32 AND bitrate_kbps <= 320),
    CONSTRAINT chk_audio_media_status CHECK (status IN ('pending', 'processing', 'ready', 'failed'))
);

COMMENT ON TABLE media_service.audio_media IS 'Siêu dữ liệu tệp âm thanh thuyết minh lưu trữ trên cụm MinIO';
COMMENT ON COLUMN media_service.audio_media.localization_id IS 'Khóa ngoại logic sang bảng localization';
COMMENT ON COLUMN media_service.audio_media.storage_path IS 'Đường dẫn object key trên MinIO bucket audio-media';
COMMENT ON COLUMN media_service.audio_media.status IS 'Trạng thái xử lý file âm thanh (pending, processing, ready, failed)';

-- ----------------------------------------------------------------------------
-- CHỈ MỤC TỐI ƯU HÓA HIỆU NĂNG (INDEXES)
-- ----------------------------------------------------------------------------
-- Tìm kiếm tệp âm thanh theo bản dịch (để phục vụ Streaming Service nạp chunk <= 2.0s)
CREATE INDEX IF NOT EXISTS idx_audio_media_localization_id 
ON media_service.audio_media(localization_id);

-- Giám sát các tệp âm thanh đang xử lý hoặc bị lỗi
CREATE INDEX IF NOT EXISTS idx_audio_media_status 
ON media_service.audio_media(status);
