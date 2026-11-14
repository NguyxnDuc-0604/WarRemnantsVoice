-- ============================================================================
-- ANALYTICS & METRIC SERVICE SCHEMA (metric_db / metric_service)
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Bounded Context: Thu thập và thống kê số liệu lượt nghe ẩn danh theo thời gian thực (UC5, FR-20, FR-22)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS metric_service;

SET search_path TO metric_service, public;

-- ----------------------------------------------------------------------------
-- 1. BẢNG SỐ LIỆU THỐNG KÊ LƯỢT NGHE ẨN DANH (listening_metric)
-- Lưu trữ vết truy cập không thu thập định danh cá nhân (BR-15)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metric_service.listening_metric (
    id BIGSERIAL PRIMARY KEY,                               -- Khóa chính số tự tăng tối ưu dữ liệu chuỗi thời gian
    exhibit_id UUID NOT NULL,                               -- Tham chiếu logic sang Exhibit Core Service (Khử khóa ngoại cứng)
    language_code VARCHAR(10) NOT NULL,                     -- Ngôn ngữ du khách đã chọn nghe
    listened_duration INT NOT NULL,                         -- Thời lượng thực tế du khách đã nghe (giây)
    trigger_type VARCHAR(20) NOT NULL,                      -- Phương thức kích hoạt: QR_CODE hoặc GPS_GEOFENCE
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Thời điểm sự kiện được ghi nhận

    CONSTRAINT chk_listening_duration CHECK (listened_duration >= 0),
    CONSTRAINT chk_trigger_type CHECK (trigger_type IN ('QR_CODE', 'GPS_GEOFENCE'))
);

COMMENT ON TABLE metric_service.listening_metric IS 'Lưu trữ sự kiện lượt nghe ẩn danh phục vụ thống kê phân tích';
COMMENT ON COLUMN metric_service.listening_metric.exhibit_id IS 'Khóa ngoại logic trỏ tới hiện vật được nghe';
COMMENT ON COLUMN metric_service.listening_metric.trigger_type IS 'Cách thức kích hoạt: QR_CODE hoặc GPS_GEOFENCE';

-- ----------------------------------------------------------------------------
-- CHỈ MỤC TỐI ƯU HÓA HIỆU NĂNG (INDEXES)
-- ----------------------------------------------------------------------------
-- Thống kê theo hiện vật và ngôn ngữ (Top hiện vật & Phân bố ngôn ngữ - FR-22)
CREATE INDEX IF NOT EXISTS idx_metric_exhibit_lang 
ON metric_service.listening_metric(exhibit_id, language_code);

-- Phân tích theo chuỗi thời gian (Khung giờ trong ngày, lọc theo ngày/tuần/tháng)
CREATE INDEX IF NOT EXISTS idx_metric_timestamp 
ON metric_service.listening_metric(timestamp DESC);

-- Thống kê hiệu quả phương thức kích hoạt (Tỷ lệ QR vs GPS)
CREATE INDEX IF NOT EXISTS idx_metric_trigger_type 
ON metric_service.listening_metric(trigger_type);

-- ----------------------------------------------------------------------------
-- VIEW THỐNG KÊ TỔNG HỢP CHO DASHBOARD OBSERVABILITY (UC5 & FR-22)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW metric_service.v_top_listened_exhibits AS
SELECT 
    exhibit_id,
    COUNT(*) AS total_listens,
    SUM(listened_duration) AS total_duration_seconds,
    ROUND(AVG(listened_duration), 1) AS avg_duration_seconds,
    COUNT(CASE WHEN trigger_type = 'QR_CODE' THEN 1 END) AS qr_count,
    COUNT(CASE WHEN trigger_type = 'GPS_GEOFENCE' THEN 1 END) AS gps_count
FROM metric_service.listening_metric
GROUP BY exhibit_id
ORDER BY total_listens DESC;

CREATE OR REPLACE VIEW metric_service.v_language_distribution AS
SELECT 
    language_code,
    COUNT(*) AS listen_count,
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM metric_service.listening_metric), 0), 2) AS percentage
FROM metric_service.listening_metric
GROUP BY language_code
ORDER BY listen_count DESC;
