-- ============================================================================
-- WAR REMNANTS VOICE - TOÀN BỘ CƠ SỞ DỮ LIỆU TẬP TRUNG (ALL-IN-ONE SCRIPT)
-- Đồ án: Công Nghệ Phần Mềm – Lớp DCT124C7 - Nhóm 3
-- Dự án: Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Hệ Quản trị CSDL: PostgreSQL 14+ / 16
-- ============================================================================

BEGIN;

-- Bật extension pgcrypto phục vụ tạo UUID và băm mật khẩu
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PHẦN 1: KHỞI TẠO CÁC SCHEMA THEO BOUNDED CONTEXT MICROSERVICES
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS auth_service;
CREATE SCHEMA IF NOT EXISTS exhibit_service;
CREATE SCHEMA IF NOT EXISTS localization_service;
CREATE SCHEMA IF NOT EXISTS media_service;
CREATE SCHEMA IF NOT EXISTS metric_service;

-- ============================================================================
-- PHẦN 2: DDL - AUTH SERVICE SCHEMA (auth_service)
-- ============================================================================

-- Bảng Vai trò (Roles)
CREATE TABLE IF NOT EXISTS auth_service.system_role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Quyền hạn (Permissions)
CREATE TABLE IF NOT EXISTS auth_service.system_permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Ánh xạ Vai trò - Quyền hạn
CREATE TABLE IF NOT EXISTS auth_service.role_permission (
    role_id UUID NOT NULL REFERENCES auth_service.system_role(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES auth_service.system_permission(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- Bảng Tài khoản Quản trị viên (Users)
CREATE TABLE IF NOT EXISTS auth_service.system_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role_id UUID NOT NULL REFERENCES auth_service.system_role(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Nhật ký Kiểm toán (Audit Log)
CREATE TABLE IF NOT EXISTS auth_service.audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth_service.system_user(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    target_resource VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_username ON auth_service.system_user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON auth_service.system_user(email);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON auth_service.audit_log(created_at DESC);

-- ============================================================================
-- PHẦN 3: DDL - EXHIBIT CORE SERVICE SCHEMA (exhibit_service)
-- ============================================================================

-- Bảng 1: Hiện vật trưng bày (exhibit)
CREATE TABLE IF NOT EXISTS exhibit_service.exhibit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,                       -- Mã QR identifier (T54-390, UH1-BELL...)
    title VARCHAR(255) NOT NULL,                            -- Tên tiếng Việt chính thức
    room_id VARCHAR(50) NOT NULL,                           -- OUTDOOR, ROOM-01, ROOM-02...
    latitude DECIMAL(10, 8),                                -- Vĩ độ GPS ngoài trời
    longitude DECIMAL(11, 8),                               -- Kinh độ GPS ngoài trời
    radius INT NOT NULL DEFAULT 15,                         -- Bán kính Geofence kích hoạt (mét, 5-50m)
    thumbnail_url VARCHAR(500),                             -- URL ảnh đại diện trên MinIO
    content_version INT NOT NULL DEFAULT 1,                 -- Phiên bản nội dung, tự tăng khi sửa văn bản gốc
    is_published BOOLEAN NOT NULL DEFAULT FALSE,            -- Trạng thái xuất bản
    is_active BOOLEAN NOT NULL DEFAULT TRUE,                -- Cờ Soft Delete (BR-12)
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_exhibit_radius CHECK (radius >= 5 AND radius <= 50),
    CONSTRAINT chk_exhibit_version CHECK (content_version >= 1)
);

-- Bảng 2: Nội dung nguồn tiếng Việt (content_source)
CREATE TABLE IF NOT EXISTS exhibit_service.content_source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL REFERENCES exhibit_service.exhibit(id) ON DELETE CASCADE,
    original_text TEXT,                                     -- Văn bản tiếng Việt chuẩn do cán bộ nhập hoặc ASR
    original_audio_url VARCHAR(500),                        -- File ghi âm gốc của cán bộ trên MinIO
    content_version INT NOT NULL,                           -- Phiên bản nội dung tương ứng
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_content_source_not_empty CHECK (
        original_text IS NOT NULL OR original_audio_url IS NOT NULL
    )
);

-- Bảng 5 (theo PRD): Lộ trình chuyên đề (tour_route)
CREATE TABLE IF NOT EXISTS exhibit_service.tour_route (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,                            -- Tên lộ trình
    description TEXT,                                       -- Giới thiệu ý nghĩa lộ trình
    ordered_exhibits_json JSONB NOT NULL DEFAULT '[]'::jsonb, -- Mảng UUID các hiện vật theo thứ tự
    estimated_time INT NOT NULL,                            -- Thời gian ước tính (phút)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,                -- Trạng thái kích hoạt
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_tour_route_time CHECK (estimated_time > 0)
);

-- Bảng Outbox Sự kiện (outbox_event) - Transactional Outbox Pattern
CREATE TABLE IF NOT EXISTS exhibit_service.outbox_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(50) NOT NULL DEFAULT 'EXHIBIT',
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_exhibit_code_unique ON exhibit_service.exhibit(code);
CREATE INDEX IF NOT EXISTS idx_exhibit_room_published_active ON exhibit_service.exhibit(room_id, is_published, is_active);
CREATE INDEX IF NOT EXISTS idx_exhibit_gps_coords ON exhibit_service.exhibit(latitude, longitude) WHERE latitude IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_content_source_lookup ON exhibit_service.content_source(exhibit_id, content_version DESC);
CREATE INDEX IF NOT EXISTS idx_outbox_unprocessed ON exhibit_service.outbox_event(created_at ASC) WHERE processed = FALSE;

-- ============================================================================
-- PHẦN 4: DDL - LOCALIZATION & GLOSSARY SCHEMA (localization_service)
-- ============================================================================

-- Bảng 6 (theo PRD): Từ điển chuẩn hóa thuật ngữ lịch sử (glossary)
CREATE TABLE IF NOT EXISTS localization_service.glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term_vi VARCHAR(150) UNIQUE NOT NULL,                   -- Thuật ngữ tiếng Việt nguồn
    term_en VARCHAR(150) NOT NULL,                          -- Dịch tiếng Anh chuẩn
    context_note VARCHAR(255),                              -- Ghi chú ngữ cảnh
    is_restricted BOOLEAN NOT NULL DEFAULT TRUE,            -- Bắt buộc AI tuân thủ
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 3: Bản dịch và Phụ đề đa ngôn ngữ (localization)
CREATE TABLE IF NOT EXISTS localization_service.localization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL,                               -- Tham chiếu logic sang Exhibit Service (Khử khóa ngoại vật lý)
    language_code VARCHAR(10) NOT NULL,                     -- Mã ngôn ngữ (en, fr, zh, ja, es, de, ko, ru...)
    translated_title VARCHAR(255) NOT NULL,                 -- Tiêu đề đã dịch
    translated_text TEXT NOT NULL,                          -- Nội dung đã dịch
    timestamps_json JSONB,                                  -- Mốc thời gian cuộn phụ đề
    content_version INT NOT NULL,                           -- Phiên bản nội dung
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,             -- Cán bộ đã duyệt
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Ràng buộc UQ1: Mỗi hiện vật tại 1 phiên bản chỉ có 1 bản dịch cho mỗi thứ tiếng
    CONSTRAINT uq_localization_exhibit_lang_version UNIQUE (exhibit_id, language_code, content_version)
);

CREATE INDEX IF NOT EXISTS idx_localization_lookup ON localization_service.localization(exhibit_id, language_code, content_version DESC);
CREATE INDEX IF NOT EXISTS idx_localization_review_status ON localization_service.localization(is_reviewed, language_code);
CREATE INDEX IF NOT EXISTS idx_glossary_term_vi ON localization_service.glossary(term_vi);

-- ============================================================================
-- PHẦN 5: DDL - STREAMING & MEDIA SERVICE SCHEMA (media_service)
-- ============================================================================

-- Bảng 4: Siêu dữ liệu tệp âm thanh thuyết minh (audio_media)
CREATE TABLE IF NOT EXISTS media_service.audio_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    localization_id UUID NOT NULL,                          -- Tham chiếu logic sang Localization Service (Khử khóa ngoại vật lý)
    file_url VARCHAR(500) NOT NULL,                         -- URL phát trực tiếp (MinIO HTTP Range)
    storage_path VARCHAR(255) NOT NULL,                     -- Đường dẫn object MinIO
    duration_seconds DECIMAL(8, 2) NOT NULL,                -- Thời lượng bài thuyết minh (giây)
    bitrate_kbps INT NOT NULL DEFAULT 128,                  -- Bitrate chuẩn 128 kbps
    voice_code VARCHAR(50),                                 -- Mã giọng đọc TTS
    status VARCHAR(20) NOT NULL DEFAULT 'ready',            -- pending, processing, ready, failed
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_audio_media_duration CHECK (duration_seconds > 0),
    CONSTRAINT chk_audio_media_bitrate CHECK (bitrate_kbps >= 32 AND bitrate_kbps <= 320),
    CONSTRAINT chk_audio_media_status CHECK (status IN ('pending', 'processing', 'ready', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_audio_media_localization_id ON media_service.audio_media(localization_id);
CREATE INDEX IF NOT EXISTS idx_audio_media_status ON media_service.audio_media(status);

-- ============================================================================
-- PHẦN 6: DDL - ANALYTICS & METRIC SERVICE SCHEMA (metric_service)
-- ============================================================================

-- Bảng 7: Số liệu thống kê lượt nghe ẩn danh (listening_metric)
CREATE TABLE IF NOT EXISTS metric_service.listening_metric (
    id BIGSERIAL PRIMARY KEY,
    exhibit_id UUID NOT NULL,                               -- Tham chiếu logic sang Exhibit Service (Khử khóa ngoại vật lý)
    language_code VARCHAR(10) NOT NULL,
    listened_duration INT NOT NULL,                         -- Giây
    trigger_type VARCHAR(20) NOT NULL,                      -- QR_CODE hoặc GPS_GEOFENCE
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_listening_duration CHECK (listened_duration >= 0),
    CONSTRAINT chk_trigger_type CHECK (trigger_type IN ('QR_CODE', 'GPS_GEOFENCE'))
);

CREATE INDEX IF NOT EXISTS idx_metric_exhibit_lang ON metric_service.listening_metric(exhibit_id, language_code);
CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON metric_service.listening_metric(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metric_trigger_type ON metric_service.listening_metric(trigger_type);

-- View Dashboard phục vụ UC5 & FR-22
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

-- ============================================================================
-- PHẦN 7: DỮ LIỆU KHỞI TẠO (SEED DATA)
-- ============================================================================

-- 1. Roles & Permissions & Users
INSERT INTO auth_service.system_role (id, code, name, description)
VALUES 
    ('a0000000-0000-0000-0000-000000000001', 'ADMIN', 'Quản trị viên Hệ thống', 'Toàn quyền cấu hình hệ thống, người dùng và kiểm duyệt'),
    ('a0000000-0000-0000-0000-000000000002', 'CURATOR', 'Cán bộ Bảo tàng / Biên tập viên', 'Quản lý hiện vật, kiểm duyệt phụ đề và audio đa ngôn ngữ'),
    ('a0000000-0000-0000-0000-000000000003', 'DEVOPS', 'Kỹ sư Vận hành', 'Theo dõi sức khỏe hạ tầng Microservices, RabbitMQ và Streaming')
ON CONFLICT (code) DO NOTHING;

INSERT INTO auth_service.system_permission (id, code, name, category)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'exhibit:read', 'Xem danh mục hiện vật', 'EXHIBIT'),
    ('b0000000-0000-0000-0000-000000000002', 'exhibit:write', 'Thêm sửa hiện vật', 'EXHIBIT'),
    ('b0000000-0000-0000-0000-000000000003', 'translation:review', 'Kiểm duyệt bản dịch', 'LOCALIZATION'),
    ('b0000000-0000-0000-0000-000000000004', 'glossary:manage', 'Quản lý từ điển lịch sử', 'LOCALIZATION'),
    ('b0000000-0000-0000-0000-000000000005', 'system:monitor', 'Giám sát hạ tầng & thống kê', 'SYSTEM')
ON CONFLICT (code) DO NOTHING;

INSERT INTO auth_service.system_user (id, username, email, password_hash, full_name, role_id, is_active)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'admin_baotang', 'admin@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Nguyễn Quốc Huy (Admin)', 'a0000000-0000-0000-0000-000000000001', TRUE),
    ('c0000000-0000-0000-0000-000000000002', 'curator_lan', 'curator@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Trần Thị Mai Lan (Curator)', 'a0000000-0000-0000-0000-000000000002', TRUE),
    ('c0000000-0000-0000-0000-000000000003', 'devops_lead', 'devops@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Lê Hoàng Nam (DevOps)', 'a0000000-0000-0000-0000-000000000003', TRUE)
ON CONFLICT (username) DO NOTHING;

-- 2. Glossary
INSERT INTO localization_service.glossary (id, term_vi, term_en, context_note, is_restricted)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'Chiến dịch Hồ Chí Minh', 'Ho Chi Minh Campaign', 'Chiến dịch lịch sử giải phóng miền Nam thống nhất đất nước tháng 4/1975, tuyệt đối không dịch nghĩa đen', TRUE),
    ('d0000000-0000-0000-0000-000000000002', 'Chiến dịch Điện Biên Phủ trên không', 'Airborne Dien Bien Phu Operation (Linebacker II)', 'Chiến dịch phòng không 12 ngày đêm Hà Nội năm 1972', TRUE),
    ('d0000000-0000-0000-0000-000000000003', 'Chất độc Da cam/Dioxin', 'Agent Orange / Dioxin', 'Chất độc hóa học do quân đội Mỹ rải xuống chiến trường Việt Nam', TRUE),
    ('d0000000-0000-0000-0000-000000000004', 'Pháo 175mm Vua chiến trường', 'M107 175mm "King of the Battlefield" Self-Propelled Gun', 'Pháo tầm xa của quân đội Mỹ trang bị trong chiến tranh Việt Nam', TRUE),
    ('d0000000-0000-0000-0000-000000000005', 'Ấp Bắc', 'Ap Bac Battle', 'Chiến thắng vang dội tại Tiền Giang năm 1963', TRUE),
    ('d0000000-0000-0000-0000-000000000006', 'Chuồng cọp Côn Đảo', 'Con Dao Tiger Cages', 'Khu biệt giam tra tấn tù nhân chính trị tại nhà tù Côn Đảo', TRUE),
    ('d0000000-0000-0000-0000-000000000007', 'Xe tăng T-54 số hiệu 390', 'T-54 Tank No. 390', 'Chiếc xe tăng húc đổ cổng chính Dinh Độc Lập trưa ngày 30/04/1975', TRUE),
    ('d0000000-0000-0000-0000-000000000008', 'Máy chém thời Ngô Đình Diệm', 'Guillotine under the Ngo Dinh Diem Regime', 'Dụng cụ hành quyết tàn bạo thi hành theo Luật 10/59', TRUE)
ON CONFLICT (term_vi) DO NOTHING;

-- 3. Exhibits & Sources
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES 
    ('e0000000-0000-0000-0000-000000000001', 'T54-390', 'Xe tăng T-54B số hiệu 390', 'OUTDOOR', 10.779740, 106.692350, 15, 'https://storage.baotang.vn/thumbnails/tank-t54-390.webp', 1, TRUE, TRUE),
    ('e0000000-0000-0000-0000-000000000002', 'UH1-BELL', 'Trực thăng đa năng UH-1 Iroquois (Huey)', 'OUTDOOR', 10.779600, 106.692200, 15, 'https://storage.baotang.vn/thumbnails/heli-uh1-bell.webp', 1, TRUE, TRUE),
    ('e0000000-0000-0000-0000-000000000003', 'C130-HERCULES', 'Máy bay vận tải quân sự hạng nặng C-130 Hercules', 'OUTDOOR', 10.779850, 106.692480, 20, 'https://storage.baotang.vn/thumbnails/c130-hercules.webp', 1, TRUE, TRUE),
    ('e0000000-0000-0000-0000-000000000004', 'M107-175MM', 'Pháo tự hành 175mm M107 "Vua chiến trường"', 'OUTDOOR', 10.779450, 106.692300, 15, 'https://storage.baotang.vn/thumbnails/m107-gun.webp', 1, TRUE, TRUE),
    ('e0000000-0000-0000-0000-000000000005', 'GUILLOTINE-1960', 'Máy chém thi hành Luật 10/59 thời Ngô Đình Diệm', 'ROOM-CHUNG-TICH', NULL, NULL, 15, 'https://storage.baotang.vn/thumbnails/guillotine.webp', 1, TRUE, TRUE),
    ('e0000000-0000-0000-0000-000000000006', 'DIOXIN-VICTIMS', 'Bộ tư liệu Hậu quả chất độc Da cam/Dioxin', 'ROOM-DIOXIN', NULL, NULL, 15, 'https://storage.baotang.vn/thumbnails/dioxin-room.webp', 1, TRUE, TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (id, exhibit_id, original_text, original_audio_url, content_version)
VALUES 
    ('f0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'Xe tăng T-54 số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng thiết giáp 203. Trưa ngày 30 tháng 4 năm 1975, chính chiếc xe tăng lịch sử này do Trung úy Vũ Đăng Toàn chỉ huy đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc toàn thắng của Chiến dịch Hồ Chí Minh lịch sử, non sông thu về một mối.', 'https://storage.baotang.vn/audio-raw/t54-390-vi.wav', 1),
    ('f0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'Trực thăng UH-1 là biểu tượng tác chiến cơ động trên không của quân đội Mỹ trong chiến tranh Việt Nam. Máy bay được sử dụng phổ biến trong các chiến thuật trực thăng vận, đổ bộ quân viễn chinh và bắn phá hỗ trợ hỏa lực yểm trợ mặt đất.', 'https://storage.baotang.vn/audio-raw/uh1-bell-vi.wav', 1),
    ('f0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'Máy bay vận tải C-130 Hercules là loại máy bay 4 động cơ cánh quạt phản lực cỡ lớn, được quân đội Mỹ và quân lực Việt Nam Cộng hòa sử dụng để tiếp tế vũ khí hạng nặng, chuyển quân và ném các loại bom siêu lớn phá rừng.', 'https://storage.baotang.vn/audio-raw/c130-hercules-vi.wav', 1),
    ('f0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'Pháo 175mm Vua chiến trường M107 có tầm bắn xa kỷ lục thời bấy giờ lên tới 32 km. Pháo được Mỹ triển khai tại các căn cứ hỏa lực dọc theo Vĩ tuyến 17 và đường mòn Hồ Chí Minh nhằm ngăn chặn dòng chi viện của quân dân miền Bắc.', 'https://storage.baotang.vn/audio-raw/m107-vi.wav', 1),
    ('f0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'Máy chém thời Ngô Đình Diệm do thực dân Pháp mang sang Việt Nam từ đầu thế kỷ 20, sau đó được chính quyền Ngô Đình Diệm đưa đi lưu động khắp các tỉnh miền Nam để xử tử những chiến sĩ yêu nước và đồng bào yêu hòa bình theo Đạo luật 10/59 tàn bạo.', 'https://storage.baotang.vn/audio-raw/guillotine-vi.wav', 1),
    ('f0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000006', 'Từ năm 1961 đến 1971, quân đội Mỹ đã rải gần 80 triệu lít chất diệt cỏ, phần lớn là Chất độc Da cam/Dioxin xuống miền Nam Việt Nam. Di chứng của chất độc đã để lại nỗi đau thảm khốc cho hàng triệu nạn nhân qua nhiều thế hệ.', 'https://storage.baotang.vn/audio-raw/dioxin-vi.wav', 1)
ON CONFLICT DO NOTHING;

-- 4. Tour routes
INSERT INTO exhibit_service.tour_route (id, title, description, ordered_exhibits_json, estimated_time, is_active)
VALUES 
    (
        '00000000-0000-0000-0000-000000000001',
        'Khí tài Quân sự Ngoài trời (Outdoor Military Collection)',
        'Lộ trình khám phá các khí tài quân sự hạng nặng tại sân bảo tàng: Xe tăng T-54 số hiệu 390, Trực thăng UH-1 Huey, Máy bay C-130 Hercules và Pháo 175mm.',
        '["e0000000-0000-0000-0000-000000000001", "e0000000-0000-0000-0000-000000000002", "e0000000-0000-0000-0000-000000000003", "e0000000-0000-0000-0000-000000000004"]'::jsonb,
        45,
        TRUE
    ),
    (
        '00000000-0000-0000-0000-000000000002',
        'Chứng tích Tội ác Chiến tranh & Hậu quả Da cam',
        'Lộ trình chuyên đề lịch sử sâu sắc: Trực diện trước các chứng tích chiến tranh, Đạo luật 10/59 với Máy chém và Nỗi đau di chứng da cam.',
        '["e0000000-0000-0000-0000-000000000005", "e0000000-0000-0000-0000-000000000006"]'::jsonb,
        60,
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

-- 5. Localizations
INSERT INTO localization_service.localization (
    id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed
) VALUES 
    (
        '10000000-0000-0000-0000-000000000001',
        'e0000000-0000-0000-0000-000000000001',
        'en',
        'T-54 Tank No. 390',
        'T-54 Tank No. 390 belonged to Company 4, Battalion 1, Tank Brigade 203. At noon on April 30, 1975, commanded by Lieutenant Vu Dang Toan, this historic tank crashed through the main gates of the Independence Palace, marking the complete victory of the historic Ho Chi Minh Campaign and reunifying Vietnam.',
        '[
            {"start_ms": 0, "end_ms": 4200, "text": "T-54 Tank No. 390 belonged to Company 4, Battalion 1, Tank Brigade 203."},
            {"start_ms": 4200, "end_ms": 11500, "text": "At noon on April 30, 1975, commanded by Lieutenant Vu Dang Toan, this historic tank crashed through the main gates of the Independence Palace,"},
            {"start_ms": 11500, "end_ms": 17800, "text": "marking the complete victory of the historic Ho Chi Minh Campaign and reunifying Vietnam."}
        ]'::jsonb,
        1,
        TRUE
    ),
    (
        '10000000-0000-0000-0000-000000000002',
        'e0000000-0000-0000-0000-000000000001',
        'fr',
        'Char de combat T-54 numéro 390',
        'Le char T-54 numéro 390 appartenait à la 4e compagnie, 1er bataillon, 203e brigade blindée. À midi le 30 avril 1975, sous le commandement du lieutenant Vu Dang Toan, ce char historique a défoncé les grilles principales du Palais de l''Indépendance, marquant la victoire finale de la campagne historique Ho Chi Minh.',
        '[
            {"start_ms": 0, "end_ms": 4500, "text": "Le char T-54 numéro 390 appartenait à la 4e compagnie, 1er bataillon, 203e brigade blindée."},
            {"start_ms": 4500, "end_ms": 12000, "text": "À midi le 30 avril 1975, sous le commandement du lieutenant Vu Dang Toan, ce char historique a défoncé les grilles principales du Palais de l''Indépendance,"},
            {"start_ms": 12000, "end_ms": 18200, "text": "marquant la victoire finale de la campagne historique Ho Chi Minh."}
        ]'::jsonb,
        1,
        TRUE
    ),
    (
        '10000000-0000-0000-0000-000000000003',
        'e0000000-0000-0000-0000-000000000006',
        'en',
        'Documentary Evidence of Agent Orange / Dioxin Consequences',
        'Between 1961 and 1971, the US military sprayed nearly 80 million liters of toxic defoliants, mostly Agent Orange / Dioxin, across southern Vietnam. The devastating chemical legacy continues to affect millions of victims across multiple generations.',
        '[
            {"start_ms": 0, "end_ms": 6500, "text": "Between 1961 and 1971, the US military sprayed nearly 80 million liters of toxic defoliants,"},
            {"start_ms": 6500, "end_ms": 11200, "text": "mostly Agent Orange / Dioxin, across southern Vietnam."},
            {"start_ms": 11200, "end_ms": 17500, "text": "The devastating chemical legacy continues to affect millions of victims across multiple generations."}
        ]'::jsonb,
        1,
        TRUE
    )
ON CONFLICT (exhibit_id, language_code, content_version) DO NOTHING;

-- 6. Audio Media
INSERT INTO media_service.audio_media (
    id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status
) VALUES 
    ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'https://minio.baotang.vn/audio-media/exhibits/t54-390/en_v1.mp3', 'audio-media/exhibits/t54-390/en_v1.mp3', 17.80, 128, 'en-US-GuyNeural', 'ready'),
    ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'https://minio.baotang.vn/audio-media/exhibits/t54-390/fr_v1.mp3', 'audio-media/exhibits/t54-390/fr_v1.mp3', 18.20, 128, 'fr-FR-HenriNeural', 'ready'),
    ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'https://minio.baotang.vn/audio-media/exhibits/dioxin-victims/en_v1.mp3', 'audio-media/exhibits/dioxin-victims/en_v1.mp3', 17.50, 128, 'en-US-JennyNeural', 'ready')
ON CONFLICT (id) DO NOTHING;

-- 7. Listening Metrics
INSERT INTO metric_service.listening_metric (exhibit_id, language_code, listened_duration, trigger_type, timestamp)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'en', 18, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    ('e0000000-0000-0000-0000-000000000001', 'fr', 18, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '90 minutes'),
    ('e0000000-0000-0000-0000-000000000001', 'vi', 20, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    ('e0000000-0000-0000-0000-000000000001', 'en', 15, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
    ('e0000000-0000-0000-0000-000000000002', 'en', 14, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
    ('e0000000-0000-0000-0000-000000000003', 'zh', 16, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '25 minutes'),
    ('e0000000-0000-0000-0000-000000000005', 'en', 25, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
    ('e0000000-0000-0000-0000-000000000006', 'en', 17, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
    ('e0000000-0000-0000-0000-000000000006', 'ja', 17, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '5 minutes');

COMMIT;
