-- ============================================================================
-- EXHIBIT CORE SERVICE SCHEMA (exhibit_db / exhibit_service)
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Bounded Context: Quản lý hiện vật, vị trí Geofence, nguồn thuyết minh gốc & lộ trình
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS exhibit_service;

SET search_path TO exhibit_service, public;

-- ----------------------------------------------------------------------------
-- 1. BẢNG HIỆN VẬT TRƯNG BÀY (exhibit)
-- Thực thể trung tâm quản lý định danh, mã QR, tọa độ GPS và phiên bản nội dung
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exhibit_service.exhibit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,                       -- Mã định danh (QR Identifier, VD: T54-390, UH1-BELL)
    title VARCHAR(255) NOT NULL,                            -- Tên hiện vật bằng tiếng Việt chính thức
    room_id VARCHAR(50) NOT NULL,                           -- Mã phòng/khu vực (OUTDOOR, ROOM-01, ROOM-02...)
    latitude DECIMAL(10, 8),                                -- Vĩ độ GPS (dành cho hiện vật ngoài trời)
    longitude DECIMAL(11, 8),                               -- Kinh độ GPS (dành cho hiện vật ngoài trời)
    radius INT NOT NULL DEFAULT 15,                         -- Bán kính Geofence kích hoạt (mét, từ 5m đến 30m)
    thumbnail_url VARCHAR(500),                             -- Đường dẫn ảnh đại diện trên MinIO
    content_version INT NOT NULL DEFAULT 1,                 -- Phiên bản nội dung nguồn, tự tăng khi sửa văn bản gốc
    is_published BOOLEAN NOT NULL DEFAULT FALSE,            -- Trạng thái xuất bản phục vụ khách tham quan (FR-02, BR-13)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,                -- Cờ Soft Delete (BR-12, cấm DELETE vật lý)
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_exhibit_radius CHECK (radius >= 5 AND radius <= 50),
    CONSTRAINT chk_exhibit_version CHECK (content_version >= 1)
);

COMMENT ON TABLE exhibit_service.exhibit IS 'Bảng hiện vật trưng bày cốt lõi của bảo tàng';
COMMENT ON COLUMN exhibit_service.exhibit.code IS 'Mã định danh duy nhất mã hóa trong link QR Code';
COMMENT ON COLUMN exhibit_service.exhibit.content_version IS 'Số phiên bản nội dung tiếng Việt hiện hành';
COMMENT ON COLUMN exhibit_service.exhibit.is_active IS 'Cờ Soft Delete bảo toàn toàn vẹn tham chiếu lịch sử';

-- ----------------------------------------------------------------------------
-- 2. BẢNG NỘI DUNG NGUỒN TIẾNG VIỆT (content_source)
-- Lưu trữ văn bản gốc hoặc tệp âm thanh thu âm tiếng Việt của cán bộ bảo tàng
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exhibit_service.content_source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL REFERENCES exhibit_service.exhibit(id) ON DELETE CASCADE,
    original_text TEXT,                                     -- Văn bản tiếng Việt chuẩn do cán bộ nhập hoặc ASR bóc băng
    original_audio_url VARCHAR(500),                        -- Đường dẫn file ghi âm giọng đọc gốc của cán bộ trên MinIO
    content_version INT NOT NULL,                           -- Khớp với phiên bản của exhibit lúc tải lên
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_content_source_not_empty CHECK (
        original_text IS NOT NULL OR original_audio_url IS NOT NULL
    )
);

COMMENT ON TABLE exhibit_service.content_source IS 'Lưu trữ tài liệu gốc tiếng Việt chuẩn cho từng phiên bản hiện vật';

-- ----------------------------------------------------------------------------
-- 3. BẢNG LỘ TRÌNH CHUYÊN ĐỀ (tour_route)
-- Quản lý các tuyến tham quan định sẵn theo mạch lịch sử khuyến nghị
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exhibit_service.tour_route (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,                            -- VD: Hiện vật ngoài trời, Chứng tích tội ác chiến tranh
    description TEXT,                                       -- Bối cảnh lịch sử và ý nghĩa tuyến tham quan
    ordered_exhibits_json JSONB NOT NULL DEFAULT '[]'::jsonb, -- Mảng JSON chứa danh sách exhibit_id theo thứ tự ghé thăm
    estimated_time INT NOT NULL,                            -- Thời gian ước tính hoàn thành (phút)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,                -- Trạng thái kích hoạt lộ trình
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_tour_route_time CHECK (estimated_time > 0)
);

COMMENT ON TABLE exhibit_service.tour_route IS 'Quản lý các lộ trình tham quan chuyên đề định sẵn';
COMMENT ON COLUMN exhibit_service.tour_route.ordered_exhibits_json IS 'Mảng JSON lưu thứ tự các exhibit_id: ["uuid-1", "uuid-2"]';

-- ----------------------------------------------------------------------------
-- 4. BẢNG SỰ KIỆN OUTBOX (outbox_event)
-- Thực hiện Transactional Outbox Pattern nhằm đồng bộ bất đồng bộ sang RabbitMQ
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exhibit_service.outbox_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(50) NOT NULL DEFAULT 'EXHIBIT',  -- EXHIBIT, CONTENT_SOURCE, TOUR_ROUTE
    aggregate_id UUID NOT NULL,                             -- ID của đối tượng phát sinh sự kiện
    event_type VARCHAR(100) NOT NULL,                       -- exhibit.source.created, exhibit.source.updated...
    payload JSONB NOT NULL,                                 -- Dữ liệu sự kiện định dạng JSON
    processed BOOLEAN NOT NULL DEFAULT FALSE,               -- Cờ đánh dấu đã đẩy lên RabbitMQ thành công hay chưa
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);

COMMENT ON TABLE exhibit_service.outbox_event IS 'Bảng Outbox phục vụ Transactional Outbox Pattern đảm bảo Eventual Consistency';

-- ----------------------------------------------------------------------------
-- CHỈ MỤC TỐI ƯU HÓA HIỆU NĂNG (INDEXES)
-- ----------------------------------------------------------------------------
-- Quét QR Code yêu cầu độ trễ cực thấp (<=1.5s - NFR-01)
CREATE UNIQUE INDEX IF NOT EXISTS idx_exhibit_code_unique ON exhibit_service.exhibit(code);

-- Tìm kiếm hiện vật đang hoạt động theo phòng trưng bày
CREATE INDEX IF NOT EXISTS idx_exhibit_room_published_active 
ON exhibit_service.exhibit(room_id, is_published, is_active);

-- Lọc tọa độ địa lý ngoài trời (hỗ trợ thuật toán Geofencing Haversine)
CREATE INDEX IF NOT EXISTS idx_exhibit_gps_coords 
ON exhibit_service.exhibit(latitude, longitude) 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Truy xuất nhanh nguồn văn bản theo hiện vật và phiên bản
CREATE INDEX IF NOT EXISTS idx_content_source_lookup 
ON exhibit_service.content_source(exhibit_id, content_version DESC);

-- Quản lý các sự kiện Outbox chưa xử lý để Message Relay đẩy vào RabbitMQ
CREATE INDEX IF NOT EXISTS idx_outbox_unprocessed 
ON exhibit_service.outbox_event(created_at ASC) 
WHERE processed = FALSE;

-- ----------------------------------------------------------------------------
-- TRIGGERS CẬP NHẬT THỜI GIAN
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION exhibit_service.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_exhibit_updated_at ON exhibit_service.exhibit;
CREATE TRIGGER trg_exhibit_updated_at
BEFORE UPDATE ON exhibit_service.exhibit
FOR EACH ROW EXECUTE FUNCTION exhibit_service.update_updated_at_column();

DROP TRIGGER IF EXISTS trg_tour_route_updated_at ON exhibit_service.tour_route;
CREATE TRIGGER trg_tour_route_updated_at
BEFORE UPDATE ON exhibit_service.tour_route
FOR EACH ROW EXECUTE FUNCTION exhibit_service.update_updated_at_column();
