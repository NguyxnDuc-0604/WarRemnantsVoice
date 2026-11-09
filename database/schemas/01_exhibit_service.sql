-- ============================================================
-- exhibit_db — Database riêng cho Exhibit Core Service
-- Thuộc quyền sở hữu: Exhibit & Content Management Service
-- Bảng sở hữu: exhibit, content_source, tour_route
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- BẢNG 1: EXHIBIT (Hiện vật trưng bày)
-- ============================================================
CREATE TABLE IF NOT EXISTS exhibit (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,
    title           VARCHAR(255) NOT NULL,
    title_en        VARCHAR(255),
    room_id         VARCHAR(50) NOT NULL,
    zone            VARCHAR(100) DEFAULT 'Khu trưng bày',
    period          VARCHAR(100),
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    radius          INT DEFAULT 15,
    thumbnail_url   VARCHAR(500),
    content_version INT NOT NULL DEFAULT 1,
    is_published    BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exhibit_code ON exhibit(code);
CREATE INDEX IF NOT EXISTS idx_exhibit_active ON exhibit(is_active, is_published);
CREATE INDEX IF NOT EXISTS idx_exhibit_zone ON exhibit(zone);

-- ============================================================
-- BẢNG 2: CONTENT_SOURCE (Nội dung thuyết minh tiếng Việt chuẩn)
-- ============================================================
CREATE TABLE IF NOT EXISTS content_source (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id          UUID NOT NULL REFERENCES exhibit(id) ON DELETE CASCADE,
    original_text       TEXT NOT NULL,
    original_audio_url  VARCHAR(500),
    content_version     INT NOT NULL DEFAULT 1,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_content_exhibit ON content_source(exhibit_id);

-- ============================================================
-- BẢNG 3: TOUR_ROUTE (Lộ trình tham quan chuyên đề)
-- ============================================================
CREATE TABLE IF NOT EXISTS tour_route (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                   VARCHAR(255) NOT NULL,
    description             TEXT,
    ordered_exhibits_json   JSONB NOT NULL,     -- Danh sách code hiện vật theo thứ tự
    estimated_time          INT NOT NULL DEFAULT 45, -- Phút
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tour_active ON tour_route(is_active);
