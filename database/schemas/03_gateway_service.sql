-- ============================================================
-- gateway_db — Database riêng cho Gateway & Analytics Service
-- Thuộc quyền sở hữu: API Gateway, Analytics & Observability Service
-- Bảng sở hữu: listening_metric, active_session, visitor_log
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- BẢNG 1: LISTENING_METRIC (Thống kê lượt nghe audio từ du khách)
-- ============================================================
CREATE TABLE IF NOT EXISTS listening_metric (
    id                  BIGSERIAL PRIMARY KEY,
    exhibit_id          VARCHAR(36),           -- Logical FK → exhibit_db.exhibit.id
    exhibit_code        VARCHAR(50),
    language_code       VARCHAR(10) NOT NULL,
    listened_duration   INT NOT NULL,          -- Thời lượng đã nghe (giây)
    trigger_type        VARCHAR(20) NOT NULL DEFAULT 'QR_CODE', -- 'QR_CODE' | 'GPS_GEOFENCE' | 'MANUAL'
    timestamp           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON listening_metric(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metric_exhibit ON listening_metric(exhibit_code);
CREATE INDEX IF NOT EXISTS idx_metric_lang ON listening_metric(language_code);

-- ============================================================
-- BẢNG 2: ACTIVE_SESSION (Quản lý phiên khách tham quan thời gian thực)
-- ============================================================
CREATE TABLE IF NOT EXISTS active_session (
    session_id          VARCHAR(64) PRIMARY KEY,
    visitor_id          VARCHAR(64) NOT NULL,
    current_exhibit     VARCHAR(50) DEFAULT 'HOME',
    current_language    VARCHAR(10) DEFAULT 'en',
    is_playing          BOOLEAN NOT NULL DEFAULT FALSE,
    device_type         VARCHAR(20) DEFAULT 'Mobile',
    ip_address          VARCHAR(45),
    last_ping           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    connected_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_ping ON active_session(last_ping);
CREATE INDEX IF NOT EXISTS idx_session_playing ON active_session(is_playing);

-- ============================================================
-- BẢNG 3: VISITOR_LOG (Nhật ký hành động của du khách theo thời gian)
-- ============================================================
CREATE TABLE IF NOT EXISTS visitor_log (
    id                  BIGSERIAL PRIMARY KEY,
    visitor_id          VARCHAR(64) NOT NULL,
    exhibit_code        VARCHAR(50),
    language_code       VARCHAR(10),
    device_type         VARCHAR(20),
    action              VARCHAR(100) NOT NULL,
    ip_address          VARCHAR(45),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vlog_created ON visitor_log(created_at DESC);
